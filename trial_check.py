from dist import pyarmor_init, get_license_info, get_expired_days

try:
    pyarmor_init(path=None, is_runtime=1, suffix='', advanced=0)
    code = get_license_info()['CODE']
    left_days = get_expired_days()
    if left_days == -1:
        print(f'This license for {code} is never expired')
    else:
        print(f'This license for {code} will be expired in {left_days} days')
except Exception as e:
    print(e)
