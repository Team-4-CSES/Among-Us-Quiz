const path = require("path");
const webpack = require("webpack");

module.exports = {
  entry: "./website/src/index.js",
  mode: "development",
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /(node_modules|bower_components)/,
        loader: "babel-loader",
        options: { presets: ["@babel/env"] },
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
  resolve: { extensions: ["*", ".js", ".jsx"] },
  output: {
    path: path.resolve(__dirname, "website/dist/"),
    publicPath: "/dist/",
    filename: "bundle.js",
  },
  devServer: {
    contentBase: path.join(__dirname, "website/public/"),
    port: 3000,
    publicPath: "http://localhost:3000/dist/",
    hotOnly: false,
  },
  plugins: [new webpack.HotModuleReplacementPlugin()],
};
