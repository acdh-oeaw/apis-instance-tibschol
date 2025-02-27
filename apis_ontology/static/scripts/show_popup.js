let c = new CETEI({
  ignoreFragmentId: true
});
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
    // Handle the LG element
    "lg": function(e) {
      let result = document.createElement("quote"); // Use a <div> for segments
      result.classList.add("lg");

      // Process child nodes and append
      for (let n of Array.from(e.childNodes)) {
        // Call the appropriate behavior for each child node
        let behavior = behaviors.tei[n.nodeName.toLowerCase()];
        if (behavior) {
          result.appendChild(behavior(n)); // Process child nodes based on their type
        } else {
          result.appendChild(n.cloneNode(true)); // Clone nodes that don't have specific behavior
        }
      }
      return result;
    },

    // Handle the LG element
    "l": function(e) {
      let result = document.createElement("div"); // Use a <div> for segments
      result.classList.add("l");

      // Process child nodes and append
      for (let n of Array.from(e.childNodes)) {
        // Call the appropriate behavior for each child node
        let behavior = behaviors.tei[n.nodeName.toLowerCase()];
        if (behavior) {
          result.appendChild(behavior(n)); // Process child nodes based on their type
        } else {
          result.appendChild(n.cloneNode(true)); // Clone nodes that don't have specific behavior
        }
      }
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
      for (let n of Array.from(e.childNodes)) {
        result.appendChild(n.cloneNode());
      }
      return result;
    },

    // Handle the seg element
    "seg": function(e) {
      let result = document.createElement("div"); // Use a <div> for segments
      result.classList.add("seg");

      // Process child nodes and append
      for (let n of Array.from(e.childNodes)) {
        // Call the appropriate behavior for each child node
        let behavior = behaviors.tei[n.nodeName.toLowerCase()];
        if (behavior) {
          result.appendChild(behavior(n)); // Process child nodes based on their type
        } else {
          result.appendChild(n.cloneNode(true)); // Clone nodes that don't have specific behavior
        }
      }
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
      result.innerHTML ="<span class='material-symbols-outlined'>description</span>";
      result.title = e.textContent;
      return result;
    },
  }
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
