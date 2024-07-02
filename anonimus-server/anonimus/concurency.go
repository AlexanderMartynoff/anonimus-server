package anonimus

import (
	"slices"
	"sync"
)

// RegistryMutex
type RegistryMutex struct {
	rg Registry[string, *sync.Mutex]
}

func (rmx *RegistryMutex) Lock(k string) func() {
	_, mx := rmx.rg.GetOrSet(k, &sync.Mutex{})

	mx.Lock()

	return func ()  {
		mx.Unlock()
	}
}

func (rmx *RegistryMutex) TryLock(k string) (bool, func()) {
	_, mx := rmx.rg.GetOrSet(k, &sync.Mutex{})

	ok := mx.TryLock()

	if ok {
		return ok, func ()  {
			mx.Unlock()
		}
	}

	return ok, nil
}

func NewRegistryMutex() RegistryMutex {
	return RegistryMutex{
		rg: NewRegistry[string](func(a, b *sync.Mutex) int {
			return 0
		}),
	}
}

// Registry
type Registry[K comparable, V any] struct {
	mx *sync.RWMutex
	kv map[K]V
	cmp func(a, b V) int
}

func (rg *Registry[K, V]) Get(k K) (V, bool) {
	rg.mx.RLock()
	defer rg.mx.RUnlock()

	v, ok := rg.kv[k]

	return v, ok
}

func (rg *Registry[K, V]) Set(k K, v V) {
	rg.mx.Lock()
	defer rg.mx.Unlock()

	rg.kv[k] = v
}

func (rg *Registry[K, V]) SetFromMap(kv map[K]V) {
	rg.mx.Lock()
	defer rg.mx.Unlock()

	for k, v := range kv {
		rg.kv[k] = v
	}
}

func (rg *Registry[K, V]) GetOrSet(k K, v V) (bool, V) {
	rg.mx.Lock()
	defer rg.mx.Unlock()

	if v, ok := rg.kv[k]; ok {
		return ok, v
	}

	rg.kv[k] = v

	return false, v
}

func (rg *Registry[K, V]) Delete(k K) {
	rg.mx.Lock()
	defer rg.mx.Unlock()

	delete(rg.kv, k)
}

func (rg *Registry[K, V]) List() []V {
	rg.mx.RLock()
	defer rg.mx.RUnlock()

	list := make([]V, 0, rg.Size())

	for _, v := range rg.kv {
		list = append(list, v)
	}

	slices.SortFunc(list, rg.cmp)

	return list
}

func (rg *Registry[K, V]) Map() map[K]V {
	return rg.kv
}

func (rg *Registry[K, V]) Size() int {
	rg.mx.RLock()
	defer rg.mx.RUnlock()

	return len(rg.kv)
}

func NewRegistry[K comparable, V any](cmp func(a, b V) int) Registry[K, V] {
	return Registry[K, V]{
		kv: map[K]V{},
		mx: &sync.RWMutex{},
		cmp: cmp,
	}
}
