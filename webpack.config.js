const path = require("path");
const webpack = require("webpack");

module.exports = {
  entry: "./website/client/src/index.js",
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
    path: path.resolve(__dirname, "website/client/dist/"),
    publicPath: "/dist/",
    filename: "bundle.js",
  },
  devServer: {
    historyApiFallback: true,
    contentBase: path.join(__dirname, "website/client/"),
    port: 3000,
    publicPath: "http://localhost:3000/dist/",
    hotOnly: false,
  },
  plugins: [new webpack.HotModuleReplacementPlugin()],
};
