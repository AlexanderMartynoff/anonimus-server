package anonimus

import (
	"encoding/json"
	"errors"
	"os"
	"strings"
)

type Config struct {
	Name string
	Version string
	Addr string
	Nats struct {
		Host string
	}
}

func ReadConfig(name string, dirPaths ...string) (Config, string, error) {
	config := Config{}

	for _, dirPath := range dirPaths {
		path := strings.Join([]string{dirPath, name}, "/")
		file, err := os.ReadFile(path)

		if err != nil {
			continue
		}

		err = json.Unmarshal(file, &config)

		if err == nil {
			return config, path, err
		}
	}

	return config, "nil", errors.New("can not read file")
}
