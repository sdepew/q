from bot.command_map import command_map
import boto3
from boto3.dynamodb.conditions import Key, Attr
import botocore
import os
import logging

logger = logging.getLogger()

# These are the allowed Keys
remember_options = ["music", "weather"]


def create_table(table_name=""):
    # TODO Figure out what I want to check here if this is different.
    if table_name != os.environ['REMEMBER_DDB_TABLE']:
        try:
            logger.debug("Creating Table {}".format(table_name))
            dynamodb = connect_dynamo(region='us-east-1')
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'name',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'command',
                        'KeyType': 'RANGE'  # Sort key
                    },
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'name',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'command',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
            os.environ['REMEMBER_DDB_TABLE'] = table.name
        except dynamodb.ResourceInUseException:
            return True
        else:
            return True
    else:
        return False


def connect_dynamo(region='us-east-1'):
    return boto3.resource('dynamodb', region_name=region)


def use_table():
    dynamodb = connect_dynamo(region='us-east-1')
    return dynamodb.Table(os.environ['REMEMBER_DDB_TABLE'])


def put_item_dynamo(query={}, user=""):
    '''
    :param query: list
    :param name: string
    :return: dict of updated items {'command': 'preference'}
    '''
    answers = {}
    table = use_table()
    try:
        for command, preference in query.items():
            if command.lower() in remember_options:
                response = table.update_item(
                    Key={
                        'name': user,
                        'command': command
                    },
                    UpdateExpression="set preference = :k",
                    ExpressionAttributeValues={
                        ':k': preference
                    },
                    ReturnValues="UPDATED_NEW"
                )
                answers[command] = response['Attributes']['preference']
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            create_table(os.environ['REMEMBER_DDB_TABLE'])
            table.wait_until_exists()
            put_item_dynamo(query=query, name=user)
    else:
        return answers


def get_all_prefs(user=""):
    table = use_table()
    answer = ""
    response = table.query(KeyConditionExpression=Key('name').eq(user))
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        try:
            answer += "\n".join("*{}*: {}".format(x['command'], x['preference']) for x in response['Items'])
        except botocore.exceptions.ClientError as scna_e:
            logger.error("Couldn't find data during table scan: {}".format(scna_e))
            pass
        except KeyError as scan_key_error:
            logger.debug('Unable to find data in Dynamo.'.format(scan_key_error))
            pass
    return answer


def delete_preference(to_remove={}, user=""):
    answer = ""
    removed = []
    try:
        table = use_table()
        for command, preference in to_remove.items():
            response = table.delete_item(Key={'name': user, 'command': command})
            removed.append(command)
    except botocore.exceptions.ClientError as delete_client_error:
        if delete_client_error.response['Error']['Code'] == "ConditionalCheckFailedException":
            logger.error("Client Error when delete_preference("
                         "to_remove= {}, user={}) was run.\n{}".format(to_remove,
                                                                       user,
                                                                       delete_client_error.response['Error']['Message']))
        else:
            logger.error("Something else went wrong while deleting "
                         "preference from Dynamo.: {}".format(delete_client_error.response))
    else:
        answer += "I removed {}. Use `!remember list` to see what is left. ".format(", ".join(removed))
    return answer


def read_from_dynamodb(query=[], user=""):
    user_input = dict(i.split(':') for i in query)
    table = use_table()
    commands = {}
    for command, preference in user_input.items():
        response = table.get_item(
            Key={
                'name': user,
                'command': command
            }
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            try:
                logger.debug("Item found in Dynamo:\n"
                             "User: {}\n"
                             "Command: {}\n"
                             "Preference: {}\n".format(
                                                        response['Item']['name'],
                                                        response['Item']['command'],
                                                        response['Item']['preference']))
                commands[response['Item']['command']] = response['Item']['preference']
            except botocore.exceptions.ClientError as read_e:
                logger.error("Couldn't find {} for {}: {}".format(command, user, read_e))
                continue
            except KeyError as key_error:
                logger.debug('Unable to find command {} for {} in Dynamo.'.format(command, user))
                continue
    return commands


def valid_option(query):
    user_input = dict(i.split(':') for i in query)
    valid_dict = dict(i for i in user_input.items() if i[0] in remember_options)
    return valid_dict


@command_map.register_command()
def remember(query=[], user=""):
    '''
    Have me remember command preferences for you.
    --------------------------------------------------------
    *Usage:*
    `!remember music:google weather:20170` - Add preference.
    `!remember list` - List your current preferences.
    `!remember google: delete` - Enter a command including the colon and the keyword `delete`
    Each `command:preference` set *MUST* be set in the format indicated.
    I can set preferences for: `weather`
    --------------------------------------------------------
    '''
    logger.debug("Trying to update user preferences.\nUser: {}, Query {}".format(user, query))
    if "list" in query:
        prefs = get_all_prefs(user)
        if prefs:
            response = "*Here are your preferences:*\n{}".format(prefs)
        else:
            response = "You don't have any preferences. Use `!help remember` for help creating some"
    elif 'delete' in query:
        query = [x for x in query if x.lower() != 'delete']
        user_input = valid_option(query)
        response = delete_preference(to_remove=user_input, user=user)
    elif query and valid_option(query):
        user_input = valid_option(query)
        response = "I'm awesome! I updated these:\n"
        try:
            updated_items = put_item_dynamo(user_input, user)
            if updated_items:
                for command, preference in updated_items.items():
                    response += "*{}*: {}".format(command, preference)
            else:
                response = "Yeah, I couldn't update those, come back after the Olympics."
        except Exception as e:
            logger.error("Error when updating user preferences: {}".format(e))
    else:
        # Return Error that we dont allow those.
        logger.warning("Query entered did not match any entries in list remember_options")
        return "You sure about that? I don't recognize those options."
    return response
