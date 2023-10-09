##########ENDPOINT##########
ENDPOINT_LOCAL = "http://localhost:8000/"
ENDPOINT_QA = "https://backend.az-qa.misterturing.com/"
ENDPOINT_PROD = "https://backend.az.misterturing.com/"

##########FILE##########
FILES_ACCEPTED = ['docx', 'doc', 'pdf', 'odp', 'pptx', 'xlsx', 'html']
SEND_FILE_LOCAL = ENDPOINT_LOCAL + "v4.0/upload-file"
SEND_FILE_QA = ENDPOINT_QA + "v4.0/upload-file"
SEND_FILE_PROD = ENDPOINT_PROD + "v4.0/upload-file"

SEARCH_FILE_LOCAL = ENDPOINT_LOCAL + "v4.0/detail-search-file/"
SEARCH_FILE_QA = ENDPOINT_QA + "v4.0/detail-search-file/"
SEARCH_FILE_PROD = ENDPOINT_PROD + "v4.0/detail-search-file/"

##########FOLDER##########
SEARCH_FOLDER_LOCAL = ENDPOINT_LOCAL + "v4.0/detail-search-folder/"
SEARCH_FOLDER_QA = ENDPOINT_QA + "v4.0/detail-search-folder/"
SEARCH_FOLDER_PROD = ENDPOINT_PROD + "v4.0/detail-search-folder/"