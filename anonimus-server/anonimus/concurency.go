package anonimus

import "sync"


// RegistryMutex
type RegistryMutex[K comparable] struct {
	rgr Registry[K, *sync.Mutex]
}

func (rmx *RegistryMutex[K]) Lock(k K) func() {
	_, mx := rmx.rgr.GetOrSet(k, &sync.Mutex{})

	mx.Lock()

	return func ()  {
		mx.Unlock()
	}
}

func NewRegistryMutex[K comparable]() RegistryMutex[K] {
	return RegistryMutex[K]{
		rgr: NewRegistry[K, *sync.Mutex](),
	}
}

// Registry
type Registry[K comparable, V any] struct {
	mx *sync.RWMutex
	kv map[K]V
}

func (rgr *Registry[K, V]) Get(k K) (V, bool) {
	rgr.mx.RLock()
	defer rgr.mx.RUnlock()

	v, ok := rgr.kv[k]

	return v, ok
}

func (rgr *Registry[K, V]) Set(k K, v V) {
	rgr.mx.Lock()
	defer rgr.mx.Unlock()

	rgr.kv[k] = v
}

func (rgr *Registry[K, V]) GetOrSet(k K, dv V) (bool, V) {
	rgr.mx.Lock()
	defer rgr.mx.Unlock()

	v, ok := rgr.kv[k]

	if ok {
		return ok, v
	}

	rgr.kv[k] = dv

	return ok, dv
}

func (rgr *Registry[K, V]) Delete(k K) {
	rgr.mx.Lock()
	defer rgr.mx.Unlock()

	delete(rgr.kv, k)
}

func (rgr *Registry[K, V]) List() []V {
	rgr.mx.RLock()
	defer rgr.mx.RUnlock()

	list := make([]V, 0, rgr.Size())

	for _, v := range rgr.kv {
		list = append(list, v)
	}

	return list
}

func (rgr *Registry[K, V]) Size() int {
	rgr.mx.RLock()
	defer rgr.mx.RUnlock()

	return len(rgr.kv)
}

func NewRegistry[K comparable, V any]() Registry[K, V] {
	return Registry[K, V]{
		kv: map[K]V{},
		mx: &sync.RWMutex{},
	}
}
