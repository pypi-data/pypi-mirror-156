import os

import typer

app = typer.Typer()


@app.command()
def prepackage():
    with open('./deploy.py', 'w+', encoding='utf-8') as writer:
        current_working_directory = os.getcwd()
        project_name = os.path.basename(current_working_directory)
        writer.write(f"""
            import os
            import shutil
            
            if __name__ == '__main__':
                try:
                    if os.path.exists(f'./build'): shutil.rmtree(f'./build')
                    if os.path.exists(f'./dist'): shutil.rmtree(f'./dist')
                    if os.path.exists(f'./{project_name}.egg-info'): shutil.rmtree(f'./{project_name}.egg-info')
            
                    os.system("python ./setup.py sdist bdist_wheel")
                    os.system(f'twine upload ./dist/*')
                except Exception as error:
                    print(error)

        """)

    with open('./setup.py', 'w+', encoding='utf-8') as writer:
        current_working_directory = os.getcwd()
        project_name = os.path.basename(current_working_directory)
        writer.write(f"""
            from setuptools import setup, find_packages
            import codecs
            import os
            
            here = os.path.abspath(os.path.dirname(__file__))
            
            with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
                long_description = "\\n" + fh.read()
            
            setup(
                name="{project_name}",
                version='0.0.1',
                author="jaytrairat",
                author_email="<jay.trairat@gmail.com>",
                description='{project_name}',
                long_description_content_type="text/markdown",
                long_description='',
                packages=find_packages(),
                install_requires=[''],
                keywords=['jaytrairat'],
                classifiers=["Programming Language :: Python :: 3"]
            )
        """)

    with open('./README.md', 'w+', encoding='utf-8') as writer:
        writer.write(f"{project_name}")

    print("done")


if __name__ == '__main__':
    app()
