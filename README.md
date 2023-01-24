# Welcome to Mixboard
***
## Project Setup

### 1. Set up node and npm
[Follow Guide](https://github.com/nvm-sh/nvm ) to quickly install
 `nvm`  and use different versions of node via the command line.

**Execute:**
```sh
$ nvm install 12.18.3
$ nvm use 12.18.3
$ node -v
v12.18.3
```


### 2. Create conda enviornment 
We use `conda` to install and manage our project environment. Find installer for your operating system at [Conda Documentation](https://docs.conda.io/en/latest/miniconda.html) to get started.

**Execute:**
```sh
$ conda env create -f environment.yml
$ conda activate mixboard
```

### 3. Install python dependencies

Step 2) should have added `pip` package in the project environment. We use this package to install project dependencies.

**Execute:**
```sh
$ pip install -r requirements.txt
```

### 4. Install redis

We use `redis-server` as a broker and task queuing. Follow this [installation guide](https://redis.io/docs/getting-started/installation/).

### 5. Install node modules
As a final step we run  from `npm` to add modules from `package.json`.

**Execute:**
```sh
$ nvm use 12.18.3
$ npm install
```

# Run

Always ensure that you're using right conda enviornment and node version.

#### Use Lint to fix files and find errors:
```sh
$ npm run lint
```

### Development Mode
***
#### Compiles and hot-reloads for development

```sh
$ npm run serve
```

### Production Mode
***
#### Compiles and minifies for production
```sh
$ npm run build
```
#### Executes the application
```sh
$ bash run_server.sh
```
Access the application at `https://127.0.0.1`
