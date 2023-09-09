lang = 'pt-br'

if lang == 'pt-br':
    ### MESSAGE CONSTANTS ###
    ### AUTOMATION ###
    AUTOMATION_NOT_FOUND = 'Automação não encontrada'
    AUTOMATION_DELETED = 'Automação deletada com sucesso'
    AUTOMATION_ACRONYM_ALREADY_EXISTS = 'Acronimo da automação já existe'
    AUTOMATION_NAME_ALREADY_EXISTS = 'Nome da automação já existe'
    NO_AUTOMATIONS_FOUND = 'Nenhuma automação encontrada'
    AUTOMATION_HAS_NO_STEPS = 'Automação não possui etapas'
    ERROR_DELETING_AUTOMATION = 'Erro ao deletar automação'
    ERROR_CREATING_AUTOMATION = 'Erro ao criar automação'
    ERROR_UPDATING_AUTOMATION = 'Erro ao atualizar automação'

    ### OWNER ###
    OWNER_ALREADY_EXISTS = 'Dono já existe'
    OWNER_REMOVED = 'Dono removido'
    OWNER_NOT_FOUND = 'Dono não encontrado'
    OWNERS_NOT_FOUND = 'Donos não encontrados'

    ### STEP ###
    STEP_NOT_FOUND = 'Etapa não encontrada'
    STEP_DELETED = 'Etapa deletada com sucesso'
    STEP_TOPIC_ALREADY_EXISTS = 'Tópico da etapa já existe'
    STEP_NAME_ALREADY_EXISTS = 'Nome da etapa já existe'
    STEP_ALREADY_EXISTS = 'Etapa já existe'
    STEPS_NOT_FOUND = 'Etapas não encontradas'
    ERROR_DELETING_STEP = 'Erro ao deletar etapa'
    ERROR_CREATING_STEP = 'Erro ao criar etapa'
    ERROR_UPDATING_STEP = 'Erro ao atualizar etapa'

    ### FIELD ###
    FIELD_NOT_FOUND = 'Campo não encontrado'
    FIELD_CREATED = 'Campo criado com sucesso'
    FIELD_DELETED = 'Campo deletado com sucesso'
    FIELD_UPDATED = 'Campo atualizado com sucesso'
    FIELD_ALREADY_EXISTS = 'Campo já existe'
    ERROR_DELETING_FIELD = 'Erro ao deletar campo'
    ERROR_CREATING_FIELD = 'Erro ao criar campo'
    ERROR_UPDATING_FIELD = 'Erro ao atualizar campo'

    ### ITEM ###
    ITEM_CREATED = 'Item criado'
    ITEM_SENT_TO_QUEUE = 'Item enviado para a fila {}'
    ITEM_MARKED_AS_ERROR = 'Item marcado como Erro'
    ITEM_MAX_TRY_COUNT_REACHED = 'Item atingiu o máximo de tentativas'
    ITEM_FINISHED = 'Item finalizado'
    ITEMS_NOT_FOUND = 'Itens não encontrados'
    ITEM_HISTORY_NOT_FOUND = 'Histórico do item não encontrado'
    ITEM_DELETED = 'Item deletado com sucesso'
    ITEM_ALREADY_DELETED = 'Item já deletado'
    ITEM_ALREADY_WITH_STATUS = 'Item já com status'
    ITEM_NOT_FOUND = 'Item não encontrado'
    ITEM_CANNOT_BE_DELETED = 'Item não pode ser deletado'
    ITEM_CANNOT_BE_UPDATED = 'Item não pode ser atualizado'
    ERROR_DELETING_ITEM = 'Erro ao deletar item'
    ERROR_CREATING_ITEM = 'Erro ao criar item'
    ERROR_UPDATING_ITEM = 'Erro ao atualizar item'
    FIELD_ITEM_REQUIRED = 'Campo {} é obrigatório'
    FIELD_ITEM_INVALID = 'Campo {} é inválido'
    FIELD_ITEM_INVALID_URL = 'Campo {} é inválido. URL inválida'

    ### TOKEN ###
    TOKEN_NOT_FOUND = 'Token não encontrado'
    TOKEN_IS_MISSING = 'Token está faltando'
    TOKEN_IS_INVALID = 'Token é inválido'
    INVALID_TOKEN_FORMAT = 'Formato de token inválido'
    ERR_TOKEN_GENERATE = 'Erro ao gerar token'

    ### USER ###
    UNAUTHORIZED_USER = 'Usuário não autorizado'
    USER_NOT_FOUND = 'Usuário não encontrado'

    ### SCHEMA ###
    ALPHANUMERIC_ERROR = 'Valor do campo deve ser alfanumérico'

    AUTOMATION_NAME_RANGE_ERROR = 'Campo NOME deve estar entre {min} e {max}'
    AUTOMATION_DESCRIPTION_RANGE_ERROR = 'Campo DESCRIÇÃO deve estar entre {min} e {max}'
    AUTOMATION_ACRONYM_RANGE_ERROR = 'Campo SIGLA deve estar entre {min} e {max}'

    STEP_NAME_RANGE_ERROR = 'Campo NOME deve estar entre {min} e {max}'
    STEP_DESCRIPTION_RANGE_ERROR = 'Campo DESCRIÇÃO deve estar entre {min} e {max}'
    STEP_RANGE_ERROR = 'Campo PASSO deve estar entre {min} e {max}'
    STEP_TOPIC_RANGE_ERROR = 'Campo TÓPICO deve estar entre {min} e {max}'
    STEP_TRY_COUNT_RANGE_ERROR = 'Campo TENTATIVAS deve estar entre {min} e {max}'

    FIELD_NAME_RANGE_ERROR = 'Campo NOME deve estar entre {min} e {max}'
    FIELD_ALIAS_RANGE_ERROR = 'Campo APELIDO deve estar entre {min} e {max}'
    FIELD_DESCRIPTION_RANGE_ERROR = 'Campo DESCRIÇÃO deve estar entre {min} e {max}'
    FIELD_TYPE_ERROR = 'Campo TIPO deve ser {type}'
    FIELD_REQUIRED_BOOLEAN_ERROR = 'Campo VALOR deve ser True ou False'
    FIELD_OPTIONS_RANGE_ERROR = 'Campo OPÇÕES devem ser maior que {min}'

    ### RESPONSE ###
    UNSUPPORTED_MEDIA_TYPE = 'Tipo de mídia não suportado'
    INTERNAL_SERVER_ERROR = 'Erro interno do servidor'
    BAD_REQUEST = 'Requisição inválida'

    ### CORS ###
    ORIGIN_NOT_ALLOWED = 'Origem não permitida'

else:
    ### MESSAGE CONSTANTS ###
    ### AUTOMATION ###
    AUTOMATION_NOT_FOUND = 'Automation not found'
    AUTOMATION_DELETED = 'Automation deleted'
    AUTOMATION_ACRONYM_ALREADY_EXISTS = 'Automation acronym already exists'
    AUTOMATION_NAME_ALREADY_EXISTS = 'Automation name already exists'
    NO_AUTOMATIONS_FOUND = 'No automations found'
    AUTOMATION_HAS_NO_STEPS = 'Automation has no steps'


    ### OWNER ###
    OWNER_ALREADY_EXISTS = 'Owner already exists'
    OWNER_REMOVED = 'Owner removed'
    OWNER_NOT_FOUND = 'Owner not found'
    OWNERS_NOT_FOUND = 'Owners not found'


    ### STEP ###
    STEP_NOT_FOUND = 'Step not found'
    STEP_DELETED = 'Step deleted'
    STEP_TOPIC_ALREADY_EXISTS = 'Step topic already exists'
    STEP_NAME_ALREADY_EXISTS = 'Step name already exists'
    STEP_ALREADY_EXISTS = 'Step already exists'
    STEPS_NOT_FOUND = 'Steps not found'


    ### FIELD ###
    FIELD_NOT_FOUND = 'Field not found'


    ### ITEM ###
    ITEM_CREATED = 'Item created'
    ITEM_SENT_TO_QUEUE = 'Item sent to Queue {}'
    ITEM_MARKED_AS_ERROR = 'Item marked as Error'
    ITEM_MAX_TRY_COUNT_REACHED = 'Item max try count reached'
    ITEM_FINISHED = 'Item finished'
    ITEMS_NOT_FOUND = 'Items not found'
    ITEM_HISTORY_NOT_FOUND = 'Item history not found'
    ITEM_DELETED = 'Item deleted'
    ITEM_ALREADY_DELETED = 'Item already deleted'
    ITEM_ALREADY_WITH_STATUS = 'Item already with status'
    ITEM_NOT_FOUND = 'Item not found'


    ### TOKEN ###
    TOKEN_NOT_FOUND = 'Token not found'
    TOKEN_IS_MISSING = 'Token is missing'
    TOKEN_IS_INVALID = 'Token is invalid'
    INVALID_TOKEN_FORMAT = 'Invalid token format'
    ERR_TOKEN_GENERATE = 'Error to generate token'


    ### USER ###
    UNAUTHORIZED_USER = 'Unauthorized user'
    USER_NOT_FOUND = 'User not found'


    ### SCHEMA ###
    ALPHANUMERIC_ERROR = 'Must be alphanumeric'
    STEP_RANGE_ERROR = 'Step must be between {min} and {max}'
    UNSUPPORTED_MEDIA_TYPE = 'Unsupported media type'


    ### RESONSE ###
    INTERNAL_SERVER_ERROR = 'Internal server error'
    BAD_REQUEST = 'Bad request'

    ### CORS ###
    ORIGIN_NOT_ALLOWED = 'Origin not allowed'








