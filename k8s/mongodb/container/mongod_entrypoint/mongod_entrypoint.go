package main

import (
	"bytes"
	"errors"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net"
	"os"
	"regexp"
	"syscall"
)

const (
	mongoConfFilePath         string = "/etc/mongod.conf"
	mongoConfTemplateFilePath string = "/etc/mongod.conf.template"
	hostsFilePath             string = "/etc/hosts"
)

var (
	// Use the same entrypoint as the mongo:3.4.2 image; just supply it with
	// the mongod conf file with custom params
	mongoStartCmd []string = []string{"/entrypoint.sh", "mongod", "--config",
		mongoConfFilePath}
)

// context struct stores the user input and the constraints for the specified
// input. It also stores the keyword that needs to be replaced in the template
// files.
type context struct {
	cliInput        string
	templateKeyword string
	regex           string
}

// sanity function takes the pre-defined constraints and the user inputs as
// arguments and validates user input based on regex matching
func sanity(input map[string]*context, fqdn, ip string) error {
	var format *regexp.Regexp
	for _, ctx := range input {
		format = regexp.MustCompile(ctx.regex)
		if format.MatchString(ctx.cliInput) == false {
			return errors.New(fmt.Sprintf(
				"Invalid value: '%s' for '%s'. Can be '%s'",
				ctx.cliInput,
				ctx.templateKeyword,
				ctx.regex))
		}
	}

	format = regexp.MustCompile(`[a-z0-9-.]+`)
	if format.MatchString(fqdn) == false {
		return errors.New(fmt.Sprintf(
			"Invalid value: '%s' for FQDN. Can be '%s'",
			fqdn,
			format))
	}

	if net.ParseIP(ip) == nil {
		return errors.New(fmt.Sprintf(
			"Invalid value: '%s' for IPv4. Can be a.b.c.d",
			ip))
	}

	return nil
}

// createFile function takes the pre-defined keywords, user inputs, the
// template file path and the new file path location as parameters, and
// creates a new file at file path with all the keywords replaced by inputs.
func createFile(input map[string]*context,
	template string, conf string) error {
	// read the template
	contents, err := ioutil.ReadFile(template)
	if err != nil {
		return err
	}
	// replace
	for _, ctx := range input {
		contents = bytes.Replace(contents, []byte(ctx.templateKeyword),
			[]byte(ctx.cliInput), -1)
	}
	// write
	err = ioutil.WriteFile(conf, contents, 0644)
	if err != nil {
		return err
	}
	return nil
}

// updateHostsFile takes the FQDN supplied as input to the container and adds
// an entry to /etc/hosts
func updateHostsFile(ip, fqdn string) error {
	fileHandle, err := os.OpenFile(hostsFilePath, os.O_APPEND|os.O_WRONLY,
		os.ModeAppend)
	if err != nil {
		return err
	}
	defer fileHandle.Close()
	// append
	_, err = fileHandle.WriteString(fmt.Sprintf("\n%s %s\n", ip, fqdn))
	if err != nil {
		return err
	}
	return nil
}

func main() {
	var fqdn, ip string
	input := make(map[string]*context)

	input["replica-set-name"] = &context{}
	input["replica-set-name"].regex = `[a-z]+`
	input["replica-set-name"].templateKeyword = "REPLICA_SET_NAME"
	flag.StringVar(&input["replica-set-name"].cliInput,
		"replica-set-name",
		"",
		"replica set name")

	input["port"] = &context{}
	input["port"].regex = `[0-9]{4,5}`
	input["port"].templateKeyword = "PORT"
	flag.StringVar(&input["port"].cliInput,
		"port",
		"",
		"mongodb port number")

	flag.StringVar(&fqdn, "fqdn", "", "FQDN of the MongoDB instance")
	flag.StringVar(&ip, "ip", "", "IPv4 address of the container")

	flag.Parse()
	err := sanity(input, fqdn, ip)
	if err != nil {
		log.Fatal(err)
	}

	err = createFile(input, mongoConfTemplateFilePath, mongoConfFilePath)
	if err != nil {
		log.Fatal(err)
	}

	err = updateHostsFile(ip, fqdn)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Printf("Starting Mongod....")
	err = syscall.Exec(mongoStartCmd[0], mongoStartCmd[0:], os.Environ())
	if err != nil {
		panic(err)
	}
}
