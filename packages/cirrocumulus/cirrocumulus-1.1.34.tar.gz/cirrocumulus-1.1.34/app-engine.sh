git pull
yarn install
yarn build
rm -rf ../cirrocumulus-app-engine/build
cp -r build ../cirrocumulus-app-engine/
