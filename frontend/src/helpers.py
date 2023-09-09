
def convert_error_to_tuple(error_dict):
    try:
        if 'message' in error_dict:
            message_value = error_dict['message']
            error_tuples = []
            if isinstance(message_value, dict):
                for field, values in message_value.items():
                    if isinstance(values, list) and len(values) > 0:
                        error_message = values[0]
                        error_tuples.append((field, [error_message]))
            else:
                error_tuples = message_value
            return error_tuples
    except Exception as e: ...
    return []