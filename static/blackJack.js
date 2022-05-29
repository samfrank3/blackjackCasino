// Chat -------------- CHAT--------------

var socket;
         $(document).ready(function(){
        //  socket = io.connect('http://' + document.domain + ':' + location.port + '/chess');
        socket = io.connect('//bjcasino.herokuapp.com/blackJack')

         socket.on('connect', function() {
             socket.emit('join', {});
            
          });
          socket.on('status', function(data) {
              $('#chat').val($('#chat').val() + '<' + data.msg + '>\n');
              $('#chat').scrollTop($('#chat')[0].scrollHeight);
          });
          
          socket.on('message', function(data) {
              $('#chat').val($('#chat').val() + data.msg + '\n');
              $('#chat').scrollTop($('#chat')[0].scrollHeight);
          });

          socket.on('startGame', function(data) {
            $('#chat').val($('#chat').val() + data.msg + '\n');
            
            const arrayInitialCardsA = [];
            if (data.AinitialcardsFirst != null && data.AinitialcardsSecond != null){
              arrayInitialCardsA[0] = data.AinitialcardsFirst;
              arrayInitialCardsA[1] = data.AinitialcardsSecond;
              // window.alert(arrayInitialCardsA);
              
            arrayInitialCardsA.forEach(function (i){
              if (i == '1'){
                var img = new Image(); 
                var div = document.getElementById('div4'); 
                img.src = '../static/cards/1.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img); 
              }
              if (i  == '2'){
                var img = new Image(); 
                var div = document.getElementById('div4'); 
                img.src = '../static/cards/2.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img); 
              } if (i  == '3'){
                var img = new Image(); 
                var div = document.getElementById('div4'); 
                img.src = '../static/cards/3.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img); 
              } if (i  == '4'){
                var img = new Image(); 
                var div = document.getElementById('div4'); 
                img.src = '../static/cards/4.png';
                div.classList.add('img', 'newimg');
                div.appendChild(img); 
              } if (i  == '5'){
                var img = new Image(); 
                var div = document.getElementById('div4'); 
                img.src = '../static/cards/5.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img); 
              } if (i  == '6'){
                var img = new Image(); 
                var div = document.getElementById('div4'); 
                img.src = '../static/cards/6.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img);
              } if (i  == '7'){
                var img = new Image(); 
                var div = document.getElementById('div4'); 
                img.src = '../static/cards/7.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img);
              } if (i  == '9'){
                var img = new Image(); 
                var div = document.getElementById('div4'); 
                img.src = '../static/cards/9.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img);
              } if (i  == '8'){
                var img = new Image(); 
                var div = document.getElementById('div4'); 
                img.src = '../static/cards/8.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img);
              } if (i  == '10'){
                var img = new Image(); 
                var div = document.getElementById('div4'); 
                img.src = '../static/cards/10.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img);
              } if (i  == '11'){
                var img = new Image(); 
                var div = document.getElementById('div4'); 
                img.src = '../static/cards/11.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img);
              }
            });
            }
           

            const arrayInitialCardsB = [];
            if (data.BinitialcardsFirst != null && data.BinitialcardsSecond != null){
              arrayInitialCardsB[0] = data.BinitialcardsFirst;
              arrayInitialCardsB[1] = data.BinitialcardsSecond;
              
              arrayInitialCardsB.forEach(function (i){
              if (i == '1'){
                var img = new Image(); 
                var div = document.getElementById('div5'); 
                img.src = '../static/cards/1.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img); 
              }
              if (i  == '2'){
                var img = new Image(); 
                var div = document.getElementById('div5'); 
                img.src = '../static/cards/2.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img); 
              } if (i  == '3'){
                var img = new Image(); 
                var div = document.getElementById('div5'); 
                img.src = '../static/cards/3.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img); 
              } if (i  == '4'){
                var img = new Image(); 
                var div = document.getElementById('div5'); 
                img.src = '../static/cards/4.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img); 
              } if (i  == '5'){
                var img = new Image(); 
                var div = document.getElementById('div5'); 
                img.src = '../static/cards/5.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img); 
              } if (i  == '6'){
                var img = new Image(); 
                var div = document.getElementById('div5'); 
                img.src = '../static/cards/6.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img);
              } if (i  == '7'){
                var img = new Image(); 
                var div = document.getElementById('div5'); 
                img.src = '../static/cards/7.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img);
              } if (i  == '9'){
                var img = new Image(); 
                var div = document.getElementById('div5'); 
                img.src = '../static/cards/9.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img);
              } if (i  == '8'){
                var img = new Image(); 
                var div = document.getElementById('div5'); 
                img.src = '../static/cards/8.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img);
              } if (i  == '10'){
                var img = new Image(); 
                var div = document.getElementById('div5'); 
                img.src = '../static/cards/10.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img);
              } if (i  == '11'){
                var img = new Image(); 
                var div = document.getElementById('div5'); 
                img.src = '../static/cards/11.png';
                img.classList.add('img', 'newimg');
                div.appendChild(img);
              }
            });
            }

            $('#chat').scrollTop($('#chat')[0].scrollHeight);
          });

          var playerAnewcard;
          var playerBnewcard;
          socket.on('hitGame', function(data) {
            $('#chat').val($('#chat').val() + data.msg  + '\n');

            //data.playerAnewcard is a string and is the value that the user has hitted and passed into javascript.
            // playerAnewcard = data.playerAnewcard;
            // playerBnewcard = data.playerBnewcard;

            //Hit Cards
            var img = new Image(); 
            var div = document.getElementById('div4'); 
            if (data.playerAnewcard == '1'){
              img.src = '../static/cards/1.png';
              img.classList.add('img', 'newimg');
              div.appendChild(img); 
            } else if (data.playerAnewcard == '2'){
              img.src = '../static/cards/2.png';
              img.classList.add('img', 'newimg');
              div.appendChild(img);
            }else if (data.playerAnewcard == '3'){
              img.src = '../static/cards/3.png';
              img.classList.add('img', 'newimg');
              div.appendChild(img);
            }else if (data.playerAnewcard == '4'){
              img.src = '../static/cards/4.png';
              img.classList.add('img', 'newimg');
              div.appendChild(img);
            }else if (data.playerAnewcard == '5'){
              img.src = '../static/cards/5.png';
              img.classList.add('img', 'newimg');
              div.appendChild(img);
            }else if (data.playerAnewcard == '6'){
              img.src = '../static/cards/6.png';
              img.classList.add('img', 'newimg');
              div.appendChild(img);
            }else if (data.playerAnewcard == '7'){
              img.src = '../static/cards/7.png';
              img.classList.add('img', 'newimg');
              div.appendChild(img);
            }else if (data.playerAnewcard == '9'){
              img.src = '../static/cards/9.png';
              img.classList.add('img', 'newimg');
              div.appendChild(img);
            }else if (data.playerAnewcard == '8'){
              img.src = '../static/cards/8.png';
              img.classList.add('img', 'newimg');
              div.appendChild(img);
            }else if (data.playerAnewcard == '10'){
              img.src = '../static/cards/10.png';
              img.classList.add('img', 'newimg');
              div.appendChild(img);
            }else if (data.playerAnewcard == '11'){
              img.src = '../static/cards/11.png';
              img.classList.add('img', 'newimg');
              div.appendChild(img);
            } else if (data.playerAnewcard == 'x'){
              //If it is game over, then we clear the div.
              document.getElementById("div4").innerHTML = "";
              //do nothing...
            }

            var img = new Image(); 
            var div2 = document.getElementById('div5'); 
            if (data.playerBnewcard == '1'){
              img.src = '../static/cards/1.png';
              img.classList.add('img', 'newimg');
              div2.appendChild(img);
            } else if (data.playerBnewcard == '2'){
              img.src = '../static/cards/2.png';
              img.classList.add('img', 'newimg');
              div2.appendChild(img);
            }else if (data.playerBnewcard == '3'){
              img.src = '../static/cards/3.png';
              img.classList.add('img', 'newimg');
              div2.appendChild(img);
            }else if (data.playerBnewcard == '4'){
              img.src = '../static/cards/4.png';
              img.classList.add('img', 'newimg');
              div2.appendChild(img);
              
            }else if (data.playerBnewcard == '5'){
              img.src = '../static/cards/5.png';
              img.classList.add('img', 'newimg');
              div2.appendChild(img);
            }else if (data.playerBnewcard == '6'){
              img.src = '../static/cards/6.png';
              img.classList.add('img', 'newimg');
              div2.appendChild(img);
            }else if (data.playerBnewcard == '7'){
              img.src = '../static/cards/7.png';
              img.classList.add('img', 'newimg');
              div2.appendChild(img);
            }else if (data.playerBnewcard == '9'){
              img.src = '../static/cards/9.png';
              img.classList.add('img', 'newimg');
              div2.appendChild(img);
            }else if (data.playerBnewcard == '8'){
              img.src = '../static/cards/8.png';
              img.classList.add('img', 'newimg');
              div2.appendChild(img);
            }else if (data.playerBnewcard == '10'){
              img.src = '../static/cards/10.png';
              img.classList.add('img', 'newimg');
              div2.appendChild(img);
            }else if (data.playerBnewcard == '11'){
              img.src = '../static/cards/11.png';
              img.classList.add('img', 'newimg');
              div2.appendChild(img);
            } else if (data.playerAnewcard == 'x'){
              document.getElementById("div5").innerHTML = "";
              //do nothing...
            }
            

            if(data.tempwinner != null){
              document.getElementById("playerAstatus").value = data.tempwinner;
              document.getElementById("playerBstatus").value = data.tempwinner;
            }
           
            $('#chat').scrollTop($('#chat')[0].scrollHeight);
          });

        

          socket.on('stayGame', function(data) {
            $('#chat').val($('#chat').val() + data.msg  + '\n');
            
           

            if (data.GameOver == 1){
              // document.getElementById("playerAscore").value = data.whowins;
              // document.getElementById("playerBscore").value = data.whowins;
              var whoeverwins = data.whowins;

              if (confirm("Game Over! " + whoeverwins + " Wins!")){
                socket.emit('gameover', {}, function() {
                  window.location.href = "/login";
                  socket.disconnect();
            });

              } else {
                socket.emit('gameover', {}, function() {
                  window.location.href = "/login";
                  socket.disconnect();
            });
              }
            }

            if (data.playerAscore != null && data.playerBscore != null){
              document.getElementById("playerAscore").value = data.playerAscore;
              document.getElementById("playerBscore").value = data.playerBscore;  
            }

            if(data.tempwinner != null){
              document.getElementById("playerAstatus").value = data.tempwinner;
              document.getElementById("playerBstatus").value = data.tempwinner;
            }
           
            $('#chat').scrollTop($('#chat')[0].scrollHeight);
          });
         
          $('#send').click(function(e) {
                  text = $('#text').val();
                  $('#text').val('');
                  socket.emit('text', {msg: text});
          });


        $('#hit').click(function(e) {
            socket.emit('hit', {});//emit 'hit' where 'hit' is defined in the python file.
            // console.log("Hit this shit!");
        });
        
        $('#stay').click(function(e) {
            socket.emit('stay', {});//emit 'stay' where 'stay' is defined in the python file.
            // console.log("Stay this shit!");
        });

        });


// Game  -------------- NEED TO WORK ON THIS..... -------------------

// Things need to work on:
//1. Make it multipleplayer supportive (Maybe to 3 or 4 people)
//2. Removew restart button once one player clicked
//3. fixed he update() function such that if there's 3 or 4 people and if one of the player wins, the top point getter wins.

// Create a local dictoinary that stores the cards (hits) and the user's moves and then pass it on to the server.