const express = require("express");
const path = require("path");
const app = express();
let bodyParser = require("body-parser");

let port = process.env.PORT || "5000";

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());


app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname+'/index.html'));
});


app.listen(port, () => {
    console.log(`App Running at http://localhost:${port}`);
})

