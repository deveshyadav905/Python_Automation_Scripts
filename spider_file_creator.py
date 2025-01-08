import os
import sys
from pathlib import Path
file_creator_path = Path(__file__).resolve()
sys.path.insert(0, str(file_creator_path.parent.parent))
BASE_PATH = os.getcwd()
from crawlers.settings import feed_folder, SPIDER_FILE_FORMATE

def spider_file_creator(spider_name,logger = None):
    class_name = spider_name
    spider_status = None
    if not (class_name[0].isdigit()):
        if '_' in spider_name:
            classname = spider_name.split('_')
            class_name = ''.join([name.capitalize() for name in classname])
        else:
            class_name = class_name.title()
        try:
            file_path = f"{BASE_PATH + feed_folder}/{class_name}.py"
            if not os.path.exists(file_path):
                with open(f'{BASE_PATH + feed_folder}/{class_name}.py', 'w') as spider_feed_file:
                    feed_file = SPIDER_FILE_FORMATE.format(class_name=class_name, spider_name=spider_name)
                    spider_feed_file.write(feed_file)
                    spider_feed_file.close()
                    spider_status = True
                    logger.info(f'Feed File created successfully: {class_name}.py')
            else:
                raise FileExistsError(f"Feed File {class_name}.py already exists.")
        except Exception as e:
                logger.error(f"Error creating Feed File {class_name}.py: {e}")

        
        if spider_status:
            git_command = f'''git add feeds_crawler/crawlers/spiders/{class_name}.py && git commit -m "Added new spider '{spider_name}'"\n'''
            with open(BASE_PATH + "/spiders_data/commit.sh", 'a') as outfile:
                outfile.write(git_command)
                logger.info(git_command)
    else:
        raise ValueError(f"Spider's name should not start with integers!")

# if __name__ == "__main__":
    # try:
    #     spider_file_creator(spider_name="devesh_dev")
    # except Exception as e:
    #     logger.error(f"An error occurred: {e}")

