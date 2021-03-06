import os

dir_path = "./Books"
with open('README.md', 'w') as outfile:
    table_of_contents = []

    # merge readme
    for file_name in os.listdir(dir_path):
        if ".md" in file_name:
                print(file_name)
                print("======")
                with open(dir_path + "/" + file_name) as chapter_md:
                    first_line = chapter_md.readline().rstrip()
                    table_of_contents.append([first_line, dir_path + "/" + file_name])

    table_of_contents = sorted(table_of_contents, key = lambda x: x[1])

    # 목차 생성
    outfile.write("# 대규모 시스템 설계 기초 \n\n")
    print(table_of_contents)
    for idx, (readme_head, pwd) in enumerate(table_of_contents):

        head = readme_head[2:]
        outfile.write(f"- [{idx + 1}장. {head}]({pwd})\n")

    outfile.write("\n\n")
