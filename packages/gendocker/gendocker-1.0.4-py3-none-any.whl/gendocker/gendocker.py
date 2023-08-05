import os
import pathlib
import sys
from datetime import datetime
import typer

app = typer.Typer()


@app.command()
def gendocker(mode, container_port):
    pathlib.Path('./nginx').mkdir(parents=True, exist_ok=True)
    if mode == 'client':
        with open(f'./Dockerfile', "w+") as writer:
            writer.write('FROM node:14.16-alpine as build-stage\n')
            writer.write('WORKDIR /app\n')
            writer.write('COPY ./nginx ./nginx\n')
            writer.write('COPY ./build ./build\n')
            writer.write('FROM nginx:stable-alpine as deploy-stage\n')
            writer.write('COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf\n')
            writer.write('COPY --from=build-stage ./app/build /usr/share/nginx/html\n')
            writer.write(f'EXPOSE {container_port}\n')
            writer.write('CMD ["nginx", "-g", "daemon off;"]\n')
    else:
        with open(f'./Dockerfile', "w+") as writer:
            writer.write('FROM node:14.16-alpine\n')
            writer.write('COPY ./package.json ./\n')
            writer.write('RUN npm install -g cross-env\n')
            writer.write('RUN npm install --silent --production\n')
            writer.write('RUN npm prune --production\n')
            writer.write('COPY . ./\n')
            writer.write(f'EXPOSE {container_port}\n')
            writer.write('CMD ["npm", "start"]\n')

    with open('./.dockerignore', 'w+') as writer:
        writer.write(".git\n")
        writer.write("logs\n")
        writer.write("*.log\n")
        writer.write("npm-debug.log*\n")
        writer.write("yarn-debug.log*\n")
        writer.write("yarn-error.log*\n")
        writer.write("lerna-debug.log*\n")
        writer.write("report.[0-9]*.[0-9]*.[0-9]*.[0-9]*.json\n")
        writer.write("pids\n")
        writer.write("*.pid\n")
        writer.write("*.seed\n")
        writer.write("*.pid.lock\n")
        writer.write("lib-cov\n")
        writer.write("coverage\n")
        writer.write("*.lcov\n")
        writer.write(".nyc_output\n")
        writer.write(".grunt\n")
        writer.write("bower_components\n")
        writer.write(".lock-wscript\n")
        writer.write("build/Release\n")
        writer.write("node_modules/\n")
        writer.write("jspm_packages/\n")
        writer.write("web_modules/\n")
        writer.write("*.tsbuildinfo\n")
        writer.write(".npm\n")
        writer.write(".eslintcache\n")
        writer.write(".rpt2_cache/\n")
        writer.write(".rts2_cache_cjs/\n")
        writer.write(".rts2_cache_es/\n")
        writer.write(".rts2_cache_umd/\n")
        writer.write(".node_repl_history\n")
        writer.write("*.tgz\n")
        writer.write(".yarn-integrity\n")
        writer.write(".cache\n")
        writer.write(".parcel-cache\n")
        writer.write(".next\n")
        writer.write("out\n")
        writer.write(".nuxt\n")
        writer.write("dist\n")
        writer.write(".cache/\n")
        writer.write(".serverless/\n")
        writer.write(".fusebox/\n")
        writer.write(".dynamodb/\n")
        writer.write(".tern-port\n")
        writer.write(".vscode-test\n")
        writer.write(".yarn/cache\n")
        writer.write(".yarn/unplugged\n")
        writer.write(".yarn/build-state.yml\n")
        writer.write(".yarn/install-state.gz\n")
        writer.write(".pnp.*\n")

    with open(f'./nginx/default.conf', "w+") as writer:
        writer.write('server {\n')
        writer.write('  listen 80;\n')
        writer.write('  location / {\n')
        writer.write('    root /usr/share/nginx/html;\n')
        writer.write('    index index.html index.htm;\n')
        writer.write('    try_files $uri /index.html;\n')
        writer.write('  }\n')
        writer.write('  error_page 500 502 503 504 /50x.html;\n')
        writer.write('  location = /50x.html {\n')
        writer.write('    root /usr/share/nginx/html;\n')
        writer.write('  }\n')
        writer.write('}\n')

    print(datetime.now(), ':: done')


if __name__ == '__main__':
    app()
