import os
import pathlib

import typer as typer

app = typer.Typer()


@app.command()
def preconfig(tag):
    pathlib.Path('./auto_generated').mkdir(parents=True, exist_ok=True)

    exclude = ['auto_generated', 'venv', '.idea', '.git', '__pycache__', 'preconfig', 'lib', 'result', 'build', 'dist']
    project_list = [str(name) for name in os.listdir(".") if os.path.isdir(name) and name not in exclude]

    with open(f'./auto_generated/docker-compose.yaml', "w+") as writer:
        writer.write('version: "3.9"\n')
        writer.write('services:\n')
        for project_name in project_list:
            writer.write(f'  {project_name}:\n')
            writer.write(f'    image: jaytrairat/{project_name}:{tag}\n')
            writer.write(f'    restart: always\n')
            writer.write(f'    ports:\n')
            writer.write(f'      - \"8000:80\"\n')
            writer.write(f'    deploy:\n')
            writer.write(f'      resources:\n')
            writer.write(f'        limits:\n')
            writer.write(f'          memory: 32M\n')
            writer.write(f'        reservations:\n')
            writer.write(f'          memory: 32M\n')

    with open(f'./auto_generated/reverse_proxy.txt', "w+") as writer:
        for project_name in project_list:
            writer.write(f'location /{project_name} {{\n')
            writer.write(f'    proxy_pass http://localhost:8000/;\n')
            writer.write(f'}}\n\n')
    #
    with open('./auto_generated/web.config', 'w+') as writer:
        writer.write(f'<?xml version="1.0" encoding="UTF-8"?>\n')
        writer.write(f'<configuration>\n')
        writer.write(f'  <system.webServer>\n')
        writer.write(f'    <rewrite>\n')
        writer.write(f'      <rules>\n')
        for project_name in project_list:
            writer.write(f'        <rule name="{project_name}" stopProcessing="true">\n')
            writer.write(f'          <match url="^web/{project_name}/(.*)" />\n')
            writer.write(f'          <action type="Rewrite" url="http://127.0.0.1:8000/{{R:1}}" />\n')
            writer.write(f'        </rule>\n')
        writer.write(f'      </rules>\n')
        writer.write(f'    </rewrite>\n')
        writer.write(f'  </system.webServer>\n')
        writer.write(f'</configuration>\n')


if __name__ == '__main__':
    app()
