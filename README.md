# Migration Script for Docker Registry V1 to v2

 A migration script for transfer docker repositories from a v1 registry to a v2 registry written in python.

 requires:
 ```
 pip install docker-py
 ```

## Usage

docker_registry_migration.py [-h] [-d] source dest

f.e.:
 ```
python docker_registry_migration.py -d source_v1.registry.docker.com dest_v2.registry.docker.com
 ```
 
## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request
