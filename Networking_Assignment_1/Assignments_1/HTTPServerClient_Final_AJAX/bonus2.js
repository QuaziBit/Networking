var host_addr = ""
var field = ""

// after page is completely loaded
$(document).ready(function(){

    // Own Board section
    var html_own = "<div class='info'>" +
    "<div class='carrier'><span>__</span>: Carrier</div>" +
        "<div class='battleship'><span>__</span>: Battleship</div>" +
        "<div class='cruiser'><span>__</span>: Cruiser</div>" +
        "<div class='submarine'><span>__</span>: Submarine</div>" +
        "<div class='destroyer'><span>__</span>: Destroyer</div>" +
        "<div class='opp_hit'><span>__</span>: Hit</div>" +
        "<div class='opp_move'><span>__</span>: Opponent Move</div>" +
    "</div>"
    
    // inject info elements into the span element with the .info_holder_own class
    $( ".info_holder_own" ).append(html_own);

    // Opponent Board section
    host_addr = $("#host_addr").val();

    // the info elements
    var html_opp = "<div class='info'>" +
    "<div class='carrier'><span>__</span>: Carrier</div>" +
        "<div class='battleship'><span>__</span>: Battleship</div>" +
        "<div class='cruiser'><span>__</span>: Cruiser</div>" +
        "<div class='submarine'><span>__</span>: Submarine</div>" +
        "<div class='destroyer'><span>__</span>: Destroyer</div>" +
        "<div class='hit'><span>__</span>: Hit</div>" +
        "<div class='miss'><span>__</span>: Miss</div>" +
        "<div class='server_feedback'></div>" +
    "</div>"    

    // inject info elements into the span element with the .info_holder_opp class
    $( ".info_holder_opp" ).append(html_opp);

});

// each ship in the html has function onlcik
// after user clicked the ship icon it will call this function
// and pass its id
function getThisID(id) {

    // revalidate server address
    host_addr = $("#host_addr").val();

    // save id
    field = id
    
    // field should be in this format: id_x_y
    // splitting up field into x and y, and ignoring id
    var str = field.split('_');
    var x = str[1];
    var y = str[2];

    // use ajax to do request to the server
    ajaxCall(x, y);
}


function ajaxCall(x, y)
{
    // build final url 
    var urlEnd = "/?x=" + x + "&" + "y=" + y
    var request_url = "http://" + host_addr + urlEnd;

    $.ajax({
        type: 'GET',
        url: request_url,
        data: {
            
        },
        success: function(result){

            // write HTTP status to the web page
            $( ".server_feedback" ).empty();
            $( ".server_feedback" ).append(result);

            reloadBoard(result);
        }
    });
}

function reloadBoard(result) {

    // get updated board from the server
    ajaxCallReloadOpp("/opponent_board.html");
}

// Reload opponent board
function ajaxCallReloadOpp(request)
{
    // build url
    var request_url = "http://" + host_addr + request;

    $.ajax({
        type: 'GET',
        url: request_url,
        data: {
            
        },
        success: function(result){

            // Server will send back the entire html page
            // after we have to retrieve the board by using .ship class
            var html = $(result).find('.ships_opp').html();

            // empty the span element that has .ships class
            $( ".ships_opp" ).empty();

            // inject updated board in to the span element
            $( ".ships_opp" ).append(html);
            
        }
    });
}
