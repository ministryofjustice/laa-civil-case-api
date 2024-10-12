IMAGE := ministryofjustice/tech-docs-github-pages-publisher:v4.0.0

# Use this to run a local instance of the documentation site, while editing
.PHONY: preview check

preview:
	docker run --rm \
		-v $$(pwd)/config:/app/config \
		-v $$(pwd)/source:/app/source \
		-p 4567:4567 \
		-it $(IMAGE) /usr/local/bin/preview

deploy:
	docker run --rm \
		-v $$(pwd)/config:/app/config \
		-v $$(pwd)/source:/app/source \
		-it $(IMAGE) /usr/local/bin/package
