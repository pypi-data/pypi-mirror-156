# Stud

## Example Studfile.yaml

```yaml
.variables:
  all_services:
    - foo
    - bar
    - baz
build-docker: 
  help: "Build and optionally push docker images"
  options:
    - name: -s,--services
      default: all
      nargs: '+'
      required: true
    - name: -p,--push
      action: store_true
  cmd: |
    if 'all' in services:
      services = all_services

    for service in services:
      docker build -t {service} -f src/{service}/Dockerfile .
      if push:
        docker push {service}
build-local: 
  help: "Build local versions of services"
  options:
    - name: -s,--services
      default: all
      nargs: '+'
      required: true
  cmd: |
    # notice that the all_services variable is available 
    if 'all' in services:
      services = all_services

    for service in services:
      # do build things here
```
