const { Buffer } = require('node:buffer');
const express = require('express');
const fetch = require('node-fetch');
const clientId = process.env.OAUTH_CLIENT_ID;
const clientSecret = process.env.OAUTH_CLIENT_SECRET;
const redirectUri = process.env.NOTION_AUTH_URL;
var app = express();

app.get('/', function(req, res) {
  //res.send("Hello World");
  console.log(redirectUri);
  console.log(clientId);
  console.log(clientSecret);
  console.log(req.query.code);
  if (req.query.code !== undefined) {
    const encoded = Buffer.from(`${clientId}:${clientSecret}`).toString("base64");
    fetch("https://api.notion.com/v1/oauth/token", {
        method: "POST",
        headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        Authorization: `Basic ${encoded}`,
    },
    body: JSON.stringify({
        grant_type: "authorization_code",
        code: req.query.code,
        redirect_uri: "http://localhost:8080/",
    }),
    }).then((resp) => resp.json()).then((jsonData) => {
      console.log(jsonData)
      res.send(jsonData);
    }).catch((err) => {
      console.log(err);
      res.send({error: "missing code"});
    });
  } else {
    res.send({error: "missing code"});
  }
});

app.listen(8080, function() {
  console.log("server open");
});

