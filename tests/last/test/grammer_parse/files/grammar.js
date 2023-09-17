const fs = require("fs");
const firstFollow = require("first-follow");

function generateSets(rules) {
  grammar = JSON.parse(rules);
  grammar[0]["right"][1] = '\u0000';
  let { firstSets, followSets, predictSets } = firstFollow(grammar);
  writeIntoFiles(firstSets, followSets, predictSets);
}

function writeIntoFiles(firstSets, followSets, predictSets) {
  fs.writeFile("./first.json", JSON.stringify(firstSets, null, 2), (err) => {
    if (err) {
      console.error(err);
      return;
    }
  });
  fs.writeFile("./follow.json", JSON.stringify(followSets, null, 2), (err) => {
    if (err) {
      console.error(err);
      return;
    }
  });
  fs.writeFile(
    "./predict.json",
    JSON.stringify(predictSets, null, 2),
    (err) => {
      if (err) {
        console.error(err);
        return;
      }
    }
  );
}

rules = `[
    { "left": "Program", "right": ["Declaration-list", "$"] },
    { "left": "Declaration-list", "right": ["Declaration", "Declaration-list"] },
    { "left": "Declaration-list", "right": [null] },
    {
      "left": "Declaration",
      "right": ["Declaration-initial", "Declaration-prime"]
    },
    { "left": "Declaration-initial", "right": ["Type-specifier", "ID"] },
    { "left": "Declaration-prime", "right": ["Fun-declaration-prime"] },
    { "left": "Declaration-prime", "right": ["Var-declaration-prime"] },
    { "left": "Var-declaration-prime", "right": [";"] },
    { "left": "Var-declaration-prime", "right": ["[", "NUM", "]", ";"] },
    {
      "left": "Fun-declaration-prime",
      "right": ["(", "Params", ")", "Compound-stmt"]
    },
    { "left": "Type-specifier", "right": ["int"] },
    { "left": "Type-specifier", "right": ["void"] },
    { "left": "Params", "right": ["int", "ID", "Param-prime", "Param-list"] },
    { "left": "Params", "right": ["void"] },
    { "left": "Param-list", "right": [",", "Param", "Param-list"] },
    { "left": "Param-list", "right": [null] },
    { "left": "Param", "right": ["Declaration-initial", "Param-prime"] },
    { "left": "Param-prime", "right": ["[", "]"] },
    { "left": "Param-prime", "right": [null] },
    {
      "left": "Compound-stmt",
      "right": ["{", "Declaration-list", "Statement-list", "}"]
    },
    { "left": "Statement-list", "right": ["Statement", "Statement-list"] },
    { "left": "Statement-list", "right": [null] },
    { "left": "Statement", "right": ["Expression-stmt"] },
    { "left": "Statement", "right": ["Compound-stmt"] },
    { "left": "Statement", "right": ["Selection-stmt"] },
    { "left": "Statement", "right": ["Iteration-stmt"] },
    { "left": "Statement", "right": ["Return-stmt"] },
    { "left": "Expression-stmt", "right": ["Expression", ";"] },
    { "left": "Expression-stmt", "right": ["break", ";"] },
    { "left": "Expression-stmt", "right": [";"] },
    {
      "left": "Selection-stmt",
      "right": ["if", "(", "Expression", ")", "Statement", "Else-stmt"]
    },
    { "left": "Else-stmt", "right": ["endif"] },
    { "left": "Else-stmt", "right": ["else", "Statement", "endif"] },
    {
      "left": "Iteration-stmt",
      "right": ["repeat", "Statement", "until", "(", "Expression", ")"]
    },
    { "left": "Return-stmt", "right": ["return", "Return-stmt-prime"] },
    { "left": "Return-stmt-prime", "right": [";"] },
    { "left": "Return-stmt-prime", "right": ["Expression", ";"] },
    { "left": "Expression", "right": ["Simple-expression-zegond"] },
    { "left": "Expression", "right": ["ID", "B"] },
    { "left": "B", "right": ["=", "Expression"] },
    { "left": "B", "right": ["[", "Expression", "]", "H"] },
    { "left": "B", "right": ["Simple-expression-prime"] },
    { "left": "H", "right": ["=", "Expression"] },
    { "left": "H", "right": ["G", "D", "C"] },
    {
      "left": "Simple-expression-zegond",
      "right": ["Additive-expression-zegond", "C"]
    },
    {
      "left": "Simple-expression-prime",
      "right": ["Additive-expression-prime", "C"]
    },
    { "left": "C", "right": ["Relop", "Additive-expression"] },
    { "left": "C", "right": [null] },
    { "left": "Relop", "right": ["<"] },
    { "left": "Relop", "right": ["=="] },
    { "left": "Additive-expression", "right": ["Term", "D"] },
    { "left": "Additive-expression-prime", "right": ["Term-prime", "D"] },
    { "left": "Additive-expression-zegond", "right": ["Term-zegond", "D"] },
    { "left": "D", "right": ["Addop", "Term", "D"] },
    { "left": "D", "right": [null] },
    { "left": "Addop", "right": ["+"] },
    { "left": "Addop", "right": ["-"] },
    { "left": "Term", "right": ["Factor", "G"] },
    { "left": "Term-prime", "right": ["Factor-prime", "G"] },
    { "left": "Term-zegond", "right": ["Factor-zegond", "G"] },
    { "left": "G", "right": ["*", "Factor", "G"] },
    { "left": "G", "right": [null] },
    { "left": "Factor", "right": ["(", "Expression", ")"] },
    { "left": "Factor", "right": ["ID", "Var-call-prime"] },
    { "left": "Factor", "right": ["NUM"] },
    { "left": "Var-call-prime", "right": ["(", "Args", ")"] },
    { "left": "Var-call-prime", "right": ["Var-prime"] },
    { "left": "Var-prime", "right": ["[", "Expression", "]"] },
    { "left": "Var-prime", "right": [null] },
    { "left": "Factor-prime", "right": ["(", "Args", ")"] },
    { "left": "Factor-prime", "right": [null] },
    { "left": "Factor-zegond", "right": ["(", "Expression", ")"] },
    { "left": "Factor-zegond", "right": ["NUM"] },
    { "left": "Args", "right": ["Arg-list"] },
    { "left": "Args", "right": [null] },
    { "left": "Arg-list", "right": ["Expression", "Arg-list-prime"] },
    { "left": "Arg-list-prime", "right": [",", "Expression", "Arg-list-prime"] },
    { "left": "Arg-list-prime", "right": [null] }
  ]`;

generateSets(rules);
