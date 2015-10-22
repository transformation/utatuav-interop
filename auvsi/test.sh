#!/bin/bash

# Server
cd /interop/server/

echo "Testing server..."

source venv/bin/activate
python manage.py test
server=$?
deactivate

echo -e "\n=====================================================================\n"

# Client
cd /interop/client/

echo "Testing Python 2 client..."

source venv2/bin/activate
nosetests interop
py2client=$?
deactivate

echo -e "\n=====================================================================\n"

echo "Testing Python 3 client..."

source venv3/bin/activate
nosetests interop
py3client=$?
deactivate

echo -e "\n=====================================================================\n"

# Frontend
cd /interop/server/auvsi_suas/static/auvsi_suas

echo "Testing JavaScript Frontend..."

./test_with_phantomjs.sh
frontend=$?

echo -e "\n=====================================================================\n"

exit_code=0

if [[ ${server} == "0" ]]; then
    echo "Server PASSED"
else
    echo "Server FAILED"
    exit_code=1
fi

if [[ ${py2client} == "0" ]]; then
    echo "Python 2 client PASSED"
else
    echo "Python 2 client FAILED"
    exit_code=1
fi

if [[ ${py3client} == "0" ]]; then
    echo "Python 3 client PASSED"
else
    echo "Python 3 client FAILED"
    exit_code=1
fi

if [[ ${frontend} == "0" ]]; then
    echo "JavaScript Frontend PASSED"
else
    echo "JavaScript Frontend FAILED"
    exit_code=1
fi

exit ${exit_code}
