account := 907044723842
image_tag := data-engineering-toolkit
region := us-east-2
repo_name := data_engineering

run:
	docker-compose up --build

deploy:
	aws ecr get-login-password --region $(region) --profile default | docker login \
	--username AWS --password-stdin $(account).dkr.ecr.$(region).amazonaws.com \
	&& docker buildx build --platform=linux/amd64 --rm -t $(repo_name):$(image_tag) . \
	&& docker tag $(repo_name):$(image_tag) $(account).dkr.ecr.$(region).amazonaws.com/$(repo_name):$(image_tag) \
	&& docker push $(account).dkr.ecr.$(region).amazonaws.com/$(repo_name):$(image_tag)
