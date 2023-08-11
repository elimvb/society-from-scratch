#python main.py --config_name default --repeats 1

nohup python main.py --config_name default --repeats 1 --LM gpt-3.5-turbo-16k &
nohup python main.py --config_name default --repeats 1 --LM gpt-4 &

nohup python main.py --config_name 3bad-guys --repeats 1 --LM gpt-3.5-turbo-16k &
nohup python main.py --config_name 3bad-guys-1st-instruct-only --repeats 1 --LM gpt-3.5-turbo-16k &

nohup python main.py --config_name 3bad-guys-1st-instruct-only-hate --repeats 1 --LM gpt-3.5-turbo-16k &
nohup python main.py --config_name 3bad-guys-1st-instruct-only-hate --repeats 1 --LM gpt-4 &


nohup python main.py --config_name 3bad-guys-1st-instruct-only-hate --repeats 1 --LM gpt-4 --api_key_id CCB &

nohup python main.py --config_name 3bad-guys-3bad-girls --repeats 1 --LM gpt-4 --api_key_id CCB &

nohup python main.py --config_name 3bad-guys-3bad-girls-hate --repeats 1 --LM gpt-4 --api_key_id CCB &




