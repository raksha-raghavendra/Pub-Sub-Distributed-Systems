# DS Project

## Specification

The aim is to implement distributed algorithms
## Running install following


```bash
# to execute in DS/
pip install -r requirements.txt
```

### Local Execution

The complete list of flags is:

```bash
$ cd distributedSystem/register
$ python3 run.py -v -c ../local_config.json

#open in multiple treminals
$ cd distributedSystem/node/
$ python3 run.py -v -c ../local_config.json

$ cd distributedSystem/subscriber/
$ python3 run.py -v -c ../local_config_subscriber.json

$ cd distributedSystem/publisher/
$ python3 run.py -v -c ../local_config_publisher.json                                   

optional arguments:   
    -h, --help            show this help message and exit   
    -v, --verbose         increase output verbosity   
    -d, --delay           generate a random delay to forwarding messages   
    -a {bully}, --algorithm {bully}                            
    -c CONFIG_FILE, --config_file CONFIG_FILE
                            needed a config file in json format
```


### Run on AWS EC2 instance

```bash
# SSH into the server instance
# run registery
ssh -i path_to_key_pair.pem_fle ec2-user@ip_instance
cd service/register/
python3 run.py -v -c ../local_config.json

# run nodes
ssh -i path_to_key_pair.pem_fle ec2-user@ip_instance
cd service/node/
python3 run.py -v -c ../local_config.json

#connect publishers and subscribers

```