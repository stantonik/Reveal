
const periods = [ "2019", "2020", "2021", "2022" ];

function onLoad()
{
}

function periodButton(button)
{
  button.style.background = "#3498db";

  for (var i = 0; i < periods.length; i++)
  {
    var id = periods[i] + "_button";
    if (id != button.id)
      document.getElementById(id).style.background = "";
  }
  

  document.getElementById("period-loader").style.opacity = 1;
  document.getElementById("disabled-mask").style.visibility = 'visible';
  document.getElementById("disabled-mask").style.opacity = 0.5;
  document.body.style.overflow = "hidden";
  document.body.style.height = "100%";
  document.html.style.overflow = "hidden";
  document.html.style.height = "100%";
}
