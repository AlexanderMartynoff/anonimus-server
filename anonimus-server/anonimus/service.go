package anonimus

import (
	"context"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"net/url"
	"slices"

	"github.com/nats-io/nats.go"
	"github.com/nats-io/nats.go/jetstream"
)

// Interface
type ConsumerFactoryService interface {
	Get(ctx context.Context, name string, id string) (consumerService, error)
}

type PublisherService interface {
	Publish(ctx context.Context, subject string, payload []byte, opts ...jetstream.PublishOpt) (*jetstream.PubAck, error)
	PublishMsg(ctx context.Context, msg *nats.Msg, opts ...jetstream.PublishOpt) (*jetstream.PubAck, error)
}

// SessionService
type SessionService struct {
	cookieName string
}

func (srv *SessionService) GetUser(r *http.Request) (User, error) {
	cookie, err := r.Cookie(srv.cookieName)

	if err != nil {
		return User{}, err
	}

	value, err := url.PathUnescape(cookie.Value)

	if err != nil {
		return User{}, err
	}

	user := User{}

	err = json.Unmarshal([]byte(value), &user)

	if err != nil {
		return User{}, err
	}

	return user, nil
}

func NewSessionService(cookieName string) SessionService {
	return SessionService{
		cookieName: cookieName,
	}
}

// NATS consumer service

type consumerService struct {
	cns    jetstream.Consumer
	cnsCtx jetstream.ConsumeContext

	Consume func(msg jetstream.Msg)
}

func (srv *consumerService) Stop() {
	srv.cnsCtx.Stop()
}

// msgConsumerSrvEndpoint

func (srv *consumerService) Start(_ context.Context) error {
	if srv.Consume == nil {
		return errors.New("'OnMessage' is nil")
	}

	if srv.cns == nil {
		return errors.New("consumer is nil")
	}

	cnsCtx, err := srv.cns.Consume(func(msg jetstream.Msg) {
		srv.Consume(msg)
	})

	if err != nil {
		return err
	}

	srv.cnsCtx = cnsCtx

	return nil
}

// TODO: Replace with just `CreateConsumer`, `CreateStream`?
type consumerFactoryService struct {
	js  jetstream.JetStream
	mtx RegistryMutex
}

func (srv *consumerFactoryService) Configure() error {
	return errors.ErrUnsupported
}

func (srv *consumerFactoryService) Get(ctx context.Context, name string, id string) (consumerService, error) {
	unlock := srv.mtx.Lock(name)
	defer unlock()

	csmSrv, err := srv.get(ctx, name, id)

	if err != nil {
		return consumerService{}, err
	}

	return csmSrv, nil
}

func (srv *consumerFactoryService) get(ctx context.Context, name string, id string) (consumerService, error) {
	stream, err := srv.createOrUpdateStream(ctx, name, id)

	if err != nil {
		return consumerService{}, err
	}

	csm, err := srv.createOrUpdateConsumer(ctx, id, stream)

	if err != nil {
		return consumerService{}, err
	}

	csmSrv := consumerService{
		cns: csm,
	}

	return csmSrv, nil
}

func (srv *consumerFactoryService) createOrUpdateStream(ctx context.Context, name string, id string) (jetstream.Stream, error) {
	if srv.js == nil {
		return nil, errors.New("jetstream is nil")
	}

	stream, err := srv.js.Stream(ctx, name)

	if errors.Is(err, jetstream.ErrStreamNotFound) {
		// create stream
		stream, err = srv.js.CreateStream(ctx, jetstream.StreamConfig{
			Name:     name,
			Subjects: []string{id},
		})

		log.Printf("Create stream '%s'", name)

		if err != nil {
			return nil, err
		}
	} else if err != nil {
		// other error
		return nil, err
	} else {
		// if stream already exists - just update it
		info, err := stream.Info(ctx)

		log.Printf("Existing stream '%s', subjects: '%s'", name, info.Config.Subjects)

		if err != nil {
			return nil, err
		}

		if !slices.Contains(info.Config.Subjects, id) {
			stream, err = srv.js.UpdateStream(ctx, jetstream.StreamConfig{
				Name:     name,
				Subjects: append(info.Config.Subjects, id),
			})

			log.Printf("Update stream '%s'", name)

			if err != nil {
				return nil, err
			}
		}
	}

	log.Printf("Select stream '%s'\n", name)

	return stream, nil
}

func (srv *consumerFactoryService) createOrUpdateConsumer(ctx context.Context, id string, stream jetstream.Stream) (jetstream.Consumer, error) {
	cns, err := stream.Consumer(ctx, id)

	if errors.Is(err, jetstream.ErrConsumerNotFound) {
		cns, err = stream.CreateConsumer(ctx, jetstream.ConsumerConfig{
			Durable:       id,
			Name:          id,
			AckPolicy:     jetstream.AckAllPolicy,
			DeliverPolicy: jetstream.DeliverAllPolicy,
			FilterSubject: id,
		})

		if err != nil {
			return nil, err
		}

		log.Printf("Create consumer '%s'", id)
	} else if err != nil {
		return nil, err
	}

	return cns, nil
}

// API
func NewConsumerFactoryService(js jetstream.JetStream) *consumerFactoryService {
	return &consumerFactoryService{
		js:  js,
		mtx: NewRegistryMutex(),
	}
}
