import re

with open('start.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add traceback to exception handling
old_code = '''    except Exception as e:
        logging.error("Failed to create app: %s", e)
        sys.exit(1)'''

new_code = '''    except Exception as e:
        import traceback
        logging.error("Failed to create app: %s", e)
        logging.error("Traceback: %s", traceback.format_exc())
        sys.exit(1)'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('start.py', 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('Successfully updated start.py')
else:
    print('Old code not found')
