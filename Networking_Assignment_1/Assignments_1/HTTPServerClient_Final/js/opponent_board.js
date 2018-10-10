$(document).ready(function(){
    //console.log("javascript ready: opponent board")

    var html = "<div class='info'>" +
    "<div class='carrier'><span>__</span>: Carrier</div>" +
        "<div class='battleship'><span>__</span>: Battleship</div>" +
        "<div class='cruiser'><span>__</span>: Cruiser</div>" +
        "<div class='submarine'><span>__</span>: Submarine</div>" +
        "<div class='destroyer'><span>__</span>: Destroyer</div>" +
        "<div class='hit'><span>__</span>: Hit</div>" +
        "<div class='miss'><span>__</span>: Miss</div>" +
    "</div>"
    
    $( ".info_holder" ).append(html);
});