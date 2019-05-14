import boto3

config_list = []

def get_datasources_froms3(bucketname, objectname):
    try:
        s3 = boto3.resource('s3')
        config_file = s3.Object(bucketname, objectname)

        for line in config_file.get()['Body']._raw_stream:
            #print(line)
            line = line.strip()
            if(len(line) == 0):
                continue
            config_dict = {}
            for items in line.decode().split(','):
                pair = items.split('=')
                #print(pair)
                config_dict[pair[0]] = pair[1]

            config_list.append(config_dict)
    except Exception as e:
        print(e)


def get_datasources(configlocation):
    """
    :param configlocation: is the path of the data sources config file
    :return: dictionary object of source urls
    """
    try:
        with open(configlocation,'r') as stream:
            print(stream.readline())

    except Exception as e:
        print(e)


print('Reading Config')
get_datasources_froms3('open-business-datamart', 'ConfigDataSources.txt')
print(config_list)
