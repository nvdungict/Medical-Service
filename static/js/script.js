function addNameToInput(clickedDiv) {
    var allDivs = document.querySelectorAll('.service__item');
    
    // Remove the name attribute from other divs
    allDivs.forEach(function(div) {
      if (div !== clickedDiv) {
        div.classList.remove('activated')
        var inputElement = div.querySelector('.no-input');
        inputElement.removeAttribute('name');
      }
    });

    // Set the name attribute of the clicked div's input
    var inputElement = clickedDiv.querySelector('.no-input');
    inputElement.setAttribute('name', 'service');   

    clickedDiv.classList.add('activated')
  }
