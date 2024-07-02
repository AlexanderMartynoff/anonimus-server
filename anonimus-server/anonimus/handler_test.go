package anonimus

import (
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"slices"
	"testing"
)

func TestOnlineUserHandler(t *testing.T) {
	r := httptest.NewRequest(http.MethodGet, "/api/online-user", nil)
	w := httptest.NewRecorder()

	rg := NewRegistry[string](func(a, b OnlineUser) int {
		if a.Id > b.Id {
			return 1
		}
		return -1
	})

	handler := OnlineUserHandler{
		OnlineUsers: rg,
	}

	rg.SetFromMap(map[string]OnlineUser{
		"k1": {
			Id: "1",
		},
		"k2": {
			Id: "2",
		},
		"k3": {
			Id: "3",
		},
	})

	handler.List(w, r)

	rsp := w.Result()
	defer rsp.Body.Close()

	body, err := io.ReadAll(rsp.Body)

	if err != nil {
		t.Fatal("Can't read body")
	}

	rspOnlineUsers := []OnlineUser{}

	err = json.Unmarshal(body, &rspOnlineUsers)

	if err != nil {
		t.Fatal("Can't read body")
	}

	onlineUsers := rg.List()

	if !slices.Equal(onlineUsers, rspOnlineUsers) {
		t.Fatal("Wrong online users list")
	}
}
