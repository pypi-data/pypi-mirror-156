.PHONY: upgrade-pollination-react

.PHONY: generate-frontend

.PHONY: dev-install-package

upgrade-pollination-react:
	yarn --cwd add pollination_streamlit_io/get_geometry/frontend pollination-react-io@latest
	yarn --cwd add pollination_streamlit_io/get_hbjson/frontend pollination-react-io@latest
	yarn --cwd add pollination_streamlit_io/send_geometry/frontend pollination-react-io@latest
	yarn --cwd add pollination_streamlit_io/send_hbjson/frontend pollination-react-io@latest

generate-frontend:
	yarn --cwd pollination_streamlit_io/get_geometry/frontend build
	yarn --cwd pollination_streamlit_io/get_hbjson/frontend build
	yarn --cwd pollination_streamlit_io/send_geometry/frontend build
	yarn --cwd pollination_streamlit_io/send_hbjson/frontend build

dev-install-package:
	cd examples/apps/ && \
	pip install -e ../../.