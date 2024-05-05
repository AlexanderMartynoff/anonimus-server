package anonimus

import (
	"encoding/json"
	"errors"
	"os"
	"strings"
)

type Settings struct {
	Name string
	Version string
	Addr string
	Nats struct {
		Host string
	}
}

func ReadSettings(name string, dirPaths ...string) (*Settings, string, error) {
	settings := &Settings{}

	for _, dirPath := range dirPaths {
		path := strings.Join([]string{dirPath, name}, "/")
		file, err := os.ReadFile(path)

		if err != nil {
			continue
		}

		err = json.Unmarshal(file, settings)

		if err == nil {
			return settings, path, err
		}
	}

	return settings, "nil", errors.New("can not read file")
}
