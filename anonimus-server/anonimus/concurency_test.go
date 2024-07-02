package anonimus

import "testing"
import "slices"


func TestRegistry(t *testing.T) {
	rg := NewRegistry[string](func(a, b string) int {
		return 0
	})

	rg.Set("k1", "v1")

	v, ok := rg.Get("k1")

	if !ok {
		t.Fatal("Empty value")
	}

	if v != "v1" {
		t.Fatal("Wrong value")
	}

	rg.Set("k2", "v2")

	if rg.Size() != 2 {
		t.Fatal("Wrong size")
	}

	ls := rg.List()

	for _, v := range []string{"v1", "v2"} {
		if !slices.Contains(ls, v) {
			t.Fatalf("Wrong registry items: '%s'", ls)
		}
	}
}

func TestRegistryMutex(t *testing.T) {
	mx := NewRegistryMutex()

	unlock := mx.Lock("k1")
	defer unlock()

	ok, _ := mx.TryLock("k1")

	if ok {
		t.Fatal("Lock locked mutex")
	}
}
