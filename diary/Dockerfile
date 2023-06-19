# Use the official Node.js image as the base
FROM node:20.3.0-alpine

# Set the working directory in the container
WORKDIR /diary

# Copy package.json and package-lock.json to the container
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the entire React app source code to the container
COPY ./ ./

# Build the React app
RUN npm run build

# Uses port which is used by the actual application
EXPOSE 9000

# Set the command to run the React app
CMD ["npm", "start"]
