let c = new CETEI({
  ignoreFragmentId: true
});
function processChildNodes(e, behaviors) {
  const fragment = document.createDocumentFragment();
  for (let n of Array.from(e.childNodes)) {
    const nodeName = n.nodeName.toLowerCase();
    const behavior = behaviors.tei[nodeName];
    if (behavior) {
      fragment.appendChild(behavior(n));
    } else {
      fragment.appendChild(n.cloneNode(true));
    }
  }
  return fragment;
}

let behaviors = {
  "tei": {
    "head": function(e) {
      let level = document.evaluate("count(ancestor::tei-div)", e, null, XPathResult.NUMBER_TYPE, null);
      let result = document.createElement("h" + (level.numberValue > 7 ? 7 : level.numberValue));
      for (let n of Array.from(e.childNodes)) {
        result.appendChild(n.cloneNode());
      }
      return result;
    },
    // handle quote element
    "quote": function(e) {
      // if it has a source attribute
      resultElementType = "span"
      if (e.getAttribute("source")) {
        resultElementType = "blockquote";
      }
      let result = document.createElement(resultElementType);
      result.appendChild(processChildNodes(e, behaviors));

      if (!e.getAttribute("source")) {
        result.classList.add("text-danger");
      }
      return result;
    },

    // Handle the LG element
    "lg": function(e) {
      let result = document.createElement("quote"); // Use a <div> for segments
      result.classList.add("lg");
      result.appendChild(processChildNodes(e, behaviors));
      return result;
    },
    // Handle the l element
    "l": function(e) {
      let result = document.createElement("div"); // Use a <div> for segments
      result.classList.add("l");
      result.appendChild(processChildNodes(e, behaviors));
      return result;
    },

    "lb": ["<span class=\"break\">$@n&nbsp;</span>"],

    // Hyperlink the rs tag and include type and ref in its title
    "rs": function(e) {
      let result = document.createElement("a");
      // make link open in a new page
      result.setAttribute("target", "_BLANK");
      result.setAttribute("href", "/apis/apis_ontology."+e.getAttribute("type")+"/"+e.getAttribute("ref").split(":")[1]);
      result.setAttribute("title", "type: " + e.getAttribute("type") + ", id: " + e.getAttribute("ref"));
      result.appendChild(processChildNodes(e, behaviors));
      return result;
    },

    // Handle the seg element
    "seg": function(e) {
      let result = document.createElement("div"); // Use a <div> for segments
      result.classList.add("seg");
      result.appendChild(processChildNodes(e, behaviors));
      return result;
    },

    // Handle the unclear element
    "unclear": function(e) {
      let result = document.createElement("span");
      result.classList.add("unclear");
      result.textContent = e.textContent;
      // using CSS instead
      // result.textContent = `(${e.textContent})`;

      return result;
    },

    // Show foreign tag in italics
    "foreign": function(e) {
      let result = document.createElement("span");
      result.classList.add("foreign");
      result.textContent = e.textContent;
      result.title = e.getAttribute("xml:lang")
      return result;
    },

    // Discard milestone
    "milestone": function(e) {
      return null;
    },
    // Note editorial
    // hide text and show note in a tooltip
    "note": function(e) {
      let result = document.createElement("span");
      result.classList.add("note");
      if (e.getAttribute("type") === "gloss") {
        result.appendChild(document.createTextNode(" ‹"));
        result.appendChild(processChildNodes(e, behaviors));
        result.appendChild(document.createTextNode("› "));
      } else {
        result.innerHTML ="<span class='material-symbols-outlined button'>description</span>";
        result.title = e.textContent;
      }
    return result;
    },
    "choice": function(e) {
      const result = document.createElement("span");
      const reg = e.querySelector("tei-reg");
      const orig = e.querySelector("tei-orig");
      const corr = e.querySelector("tei-corr");
      const sic = e.querySelector("tei-sic");
      console.log("CHOICE", reg, orig, corr, sic);
      let displayNode = null;
      let titleText = "";
      console.log(reg, orig, corr, sic);
      if (reg && orig) {
        displayNode = reg.cloneNode(true);

        titleText = "original: " + orig.textContent;
      } else if (corr && sic) {
        displayNode = corr.cloneNode(true);
        titleText = "sic: " + sic.textContent;
      }

      if (displayNode) {
        result.appendChild(processChildNodes(displayNode, behaviors));
        result.title = titleText;
        result.classList.add("choice");
      }

      return result;
    }  }
};

c.addBehaviors(behaviors);

function showExcerpt(recordId, renderStyle) {
  document.getElementById("popupContent").innerHTML = "";
  renderStyle = "tei";
  fetch(`/apis/excerpts/${recordId}/${renderStyle}`)
    .then(response => response.json())
    .then(teidata => {
      console.log("TEI DATA",teidata);
      // show raw teidata in the element #rawTEI as text
      document.getElementById("rawTEI").innerText = teidata.xml_content;
      document.getElementById("excerpt-id").innerText = teidata.xml_id;
      document.getElementById("excerpt-status").innerText = teidata.status;
      document.getElementById("instances").innerHTML = teidata.instances;
      document.getElementById("location").innerHTML = teidata.location;

      c.makeHTML5(teidata.xml_content, function(data) {
        document.getElementById("popupContent").appendChild(data);
        document.getElementById('popupModal').style.display = 'block';
      });

    })  .catch(error => {
      console.error('Error fetching data:', error);
      document.getElementById("popupContent").innerHTML = "Not Found";
      document.getElementById("excerpt-id").innerText = "";
      document.getElementById("excerpt-status").innerText = "";
      document.getElementById("rawTEI").innerText = "";
      document.getElementById('popupModal').style.display = 'block';
      document.getElementById("location").innerHTML = "";
      document.getElementById("instances").innerHTML = "";
      return;
    });
}

function closePopup() {
  document.getElementById('popupModal').style.display = 'none';
}

// allow popup to close on pressing escape
document.onkeydown = function(evt) {
  evt = evt || window.event;
  if (evt.keyCode == 27) {
    closePopup();
  }
};
