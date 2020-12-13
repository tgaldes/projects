coverage run -m nose
coverage report -m | grep -v tgaldes | grep -v resources | grep -v usr
