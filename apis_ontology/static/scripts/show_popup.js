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
  }
};

c.addBehaviors(behaviors);

function showPopup(recordId, renderStyle) {
  document.getElementById("popupContent").innerHTML = "";
  renderStyle = "tei";
  fetch(`/apis/excerpts/${recordId}/${renderStyle}`)
    .then(response => response.text())
    .then(teidata => {
      // show 404 error if the respose is 404
      if (teidata.includes("Page not found")) {
        document.getElementById("popupContent").innerHTML = "Excerpt Not Found";
        document.getElementById("rawTEI").innerText = "";
        document.getElementById('popupModal').style.display = 'block';
        return;
      }
      // show raw teidata in the element #rawTEI as text
      document.getElementById("rawTEI").innerText = teidata;
      console.log(teidata);
      c.makeHTML5(teidata, function(data) {
        document.getElementById("popupContent").appendChild(data);
        document.getElementById('popupModal').style.display = 'block';
      });

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

// allow vertical scroll to popup
document.getElementById('popupModal').addEventListener('wheel', function(e) {
  e.preventDefault();
  this.scrollTop += e.deltaY;
}, false);
