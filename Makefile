.PHONY: install dev build build-dev preview lint clean

install:
	npm install

dev:
	npm run dev

build:
	npm run build

build-dev:
	npm run build:dev

preview:
	npm run preview

lint:
	npm run lint

clean:
	rm -rf dist node_modules
