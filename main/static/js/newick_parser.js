function ctype_alnum (str)
{
    return (str.match(/^[a-z0-9]+$/i) != null);
}

function strip(html)
{
   var tmp = document.createElement("DIV");
   tmp.innerHTML = html;
   return tmp.textContent || tmp.innerText || "";
}

function isNumber (o) {
  return ! isNaN (o-0);
}

function Node(label) {
    this.ancestor = null;
    this.child = null;
    this.sibling = null;
    this.label = typeof label !== 'undefined' ? label : '';
    this.id = 0;
    this.weight = 0;
    this.xy = [];
    this.edge_length = 0.0;
    this.path_length = 0.0;
    this.depth = 0;
    this.order = null;
}

Node.prototype.IsLeaf = function() {
    return (!this.child);
}

function Tree() {
    this.root = null;
    this.num_leaves = 0;
    this.num_nodes = 0;
    this.nodes = [];
    this.rooted = true;
    this.has_edge_lengths = false;
    this.error = 0;
}

Tree.prototype.NewNode = function(label) {
    var node = new Node(label);
    node.id = this.num_nodes++;
    this.nodes[node.id] = node;
    return node;
}

Tree.prototype.Parse = function(str) {
    str = str.replace('"', "");

    // Strip NEXUS-style comments
    str = str.replace(/\[[^\[]+\]/g, "");

    str = str.replace(/\(/g, "|(|");
    str = str.replace(/\)/g, "|)|");
    str = str.replace(/,/g, "|,|");
    str = str.replace(/:/g, "|:|");
    str = str.replace(/;/g, "|;|");
    str = str.replace(/\|\|/g, "|");
    str = str.replace(/^\|/, "");
    str = str.replace(/\|$/, "");

    //console.log(str);

    var token = str.split("|");
    var curnode = this.NewNode();
    this.root = curnode;

    var state = 0;
    var stack = [];
    var i = 0;
    var q = null;

    this.error = 0;

    while ((state != 99) && (this.error == 0)) {
        switch (state) {
            case 0:
                if (ctype_alnum(token[i].charAt(0))) {
                    this.num_leaves++;
                    label = token[i];
                    curnode.label = label;
                    i++;
                    state = 1;
                } else {
                    if (token[i].charAt(0) == "'") {
                        label = token[i];
                        label = label.replace(/^'/, "");
                        label = label.replace(/'$/, "");
                        this.num_leaves++;
                        curnode.label = label;
                        i++;
                        state = 1;
                    } else {
                        switch (token[i]) {
                            case '(':
                                state = 2;
                                break;

                            default:
                                state = 99;
                                this.error = 1; // syntax
                                break;
                        }

                    }
                }
                break;


            case 1: // getinternode
                switch (token[i]) {
                    case ':':
                    case ',':
                    case ')':
                        state = 2;
                        break;
                    default:
                        state = 99;
                        this.error = 1; // syntax
                        break;
                }
                break;

            case 2: // nextmove
                switch (token[i]) {
                    case ':':
                        i++;
                        if (isNumber(token[i])) {
                            this.has_edge_lengths = true;
                            i++;
                        }
                        break;

                    case ',':
                        q = this.NewNode();
                        curnode.sibling = q;
                        var c = stack.length;
                        if (c == 0) {
                            state = 99;
                            this.error = 2; // missing (
                        } else {
                            q.ancestor = stack[c - 1];
                            curnode = q;
                            state = 0;
                            i++;
                        }
                        break;

                    case '(':
                        stack.push(curnode);
                        q = this.NewNode();
                        curnode.child = q;
                        q.ancestor = curnode;
                        curnode = q;
                        state = 0;
                        i++;
                        break;

                    case ')':
                        if (stack.length == 0) {
                            state = 99;
                            this.error = 3; // unbalanced
                        } else {
                            curnode = stack.pop();
                            state = 3;
                            i++;
                        }
                        break;

                    case ';':
                        if (stack.length == 0) {
                            state = 99;
                        } else {
                            state = 99;
                            this.error = 4; // stack not empty
                        }
                        break;

                    default:
                        state = 99;
                        this.error = 1; // syntax
                        break;
                }
                break;

            case 3: // finishchildren
                if (ctype_alnum(token[i].charAt(0))) {
                    curnode.label = token[i];
                    i++;
                } else {
                    switch (token[i]) {
                        case ':':
                            i++;
                            if (isNumber(token[i])) {
                                this.has_edge_lengths = true;
                                i++;
                            }
                            break;

                        case ')':
                            if (stack.length == 0) {
                                state = 99;
                                this.error = 3; // unbalanced
                            } else {
                                curnode = stack.pop();
                                i++;
                            }
                            break;

                        case ',':
                            q = this.NewNode();
                            curnode.sibling = q;

                            if (stack.length == 0) {
                                state = 99;
                                this.error = 2; // missing (
                            } else {
                                q.ancestor = stack[stack.length - 1];
                                curnode = q;
                                state = 0;
                                i++;
                            }
                            break;

                        case ';':
                            state = 2;
                            break;

                        default:
                            state = 99;
                            this.error = 1; // syntax
                            break;
                    }
                }
                break;
        }
    }
}
