/* Authored pilot curriculum. Diagrams show legal moves; only the explicitly
 * proof-checked mating exercises are scored. No expert or Pikafish claim.
 * Browser: CCCurriculum. Node: require('./curriculum.js'). */
(function(root,factory){'use strict';const api=factory(typeof module!=='undefined'&&module.exports?require('./xiangqi.js'):root.XQ);if(typeof module!=='undefined'&&module.exports)module.exports=api;root.CCCurriculum=api;})(typeof globalThis!=='undefined'?globalThis:this,function(XQ){
 'use strict';
 const start=XQ.START_FEN;
 const rook='4k4/9/r8/8p/9/4P4/9/R8/9/4K4 w';
 const cannon='4k4/9/1r7/8p/9/1H2P4/9/1C7/9/4K4 w';
 const horse='4k4/9/9/p8/3r5/4P4/2H6/9/9/4K4 w';
 const horseBlocked='3k5/9/9/9/3r5/2P6/2H6/9/9/4K4 w';
 const safety='4k4/9/9/8p/9/4P4/9/R8/9/r3K4 w';
 const safetyBlock='3k5/4r4/9/9/9/9/9/R8/9/4K4 w';
 const rookBlocked='3k5/9/9/9/9/9/R1P3r2/9/9/4K4 w';
 const palace='3aka3/9/9/6R2/9/3R5/9/9/9/3K5 w';
 const courses=[
  {id:'opening',title:'Khai cuộc',description:'Phát triển quân và đọc phản ứng đầu ván.',chapterIds:['opening-foundation']},
  {id:'middle',title:'Trung cuộc',description:'Khám phá Xe, Pháo, Mã, an toàn Tướng và phối hợp.',chapterIds:['rook','cannon','horse','kingSafety','coordination']},
  {id:'end',title:'Tàn cuộc',description:'Bắt đầu bằng việc kiểm tra đường thoát và kết thúc ván.',chapterIds:['end-basic']}
 ];
 const chapters=[
  {id:'opening-foundation',courseId:'opening',title:'Bắt đầu có kế hoạch',icon:'開',summary:'Một nước mở đầu chưa quyết định cả ván.',lessonIds:['opening-development'],exerciseIds:[],fixtureSkills:[]},
  {id:'rook',courseId:'middle',title:'Xe',icon:'俥',summary:'Đường mở, vật cản và phối hợp hai Xe.',lessonIds:['rook-open-file','rook-support'],exerciseIds:['v6-rooks-palace-a'],fixtureSkills:['material']},
  {id:'cannon',courseId:'middle',title:'Pháo',icon:'炮',summary:'Quan sát ngòi trước và sau mỗi trao đổi.',lessonIds:['cannon-screen'],exerciseIds:[],fixtureSkills:['cannon']},
  {id:'horse',courseId:'middle',title:'Mã',icon:'傌',summary:'Nhìn chân Mã và cả những đường đi lùi.',lessonIds:['horse-path'],exerciseIds:[],fixtureSkills:['horse']},
  {id:'kingSafety',courseId:'middle',title:'An toàn Tướng',icon:'帥',summary:'Giải chiếu trước khi tiếp tục kế hoạch.',lessonIds:['king-first'],exerciseIds:[],fixtureSkills:['safety']},
  {id:'coordination',courseId:'middle',title:'Phối hợp quân',icon:'合',summary:'Một quân khống chế, quân còn lại kết thúc.',lessonIds:['rooks-palace'],exerciseIds:['v6-rooks-palace-a','v6-rooks-palace-b'],fixtureSkills:[]},
  {id:'end-basic',courseId:'end',title:'Đường thoát của Tướng',icon:'終',summary:'Phân biệt hết nước hợp lệ và chiếu hết.',lessonIds:['end-escape'],exerciseIds:[],fixtureSkills:['safety']}
 ];
 const section=(title,text,fen,moves=[],caption='Minh họa hợp lệ; không phải đánh giá nước tối ưu.')=>({title,text,fen,moves,caption});
 const lessons=[
  {id:'opening-development',chapterId:'opening-foundation',phase:'opening',title:'Mở đường rồi quan sát đối thủ',summary:'Phát triển quân bằng một ý tưởng, luôn chừa chỗ cho phản ứng của bên kia.',difficulty:'beginner',sections:[
   section('Đưa Pháo vào giữa','Pháo không ăn quân đi theo hàng hoặc cột trống. Sau nước mở đầu, hãy đọc lại vị trí thay vì coi cả chuỗi tiếp theo là bắt buộc.',start,['h2e2','b9c7','h0g2']),
   section('Nhìn một hướng triển khai khác','Tiến Tốt có thể mở không gian nhưng cũng thay đổi các ô được bảo vệ. Đây là một diễn biến minh họa, không phải khai cuộc được khẳng định ưu thế.',start,['c3c4','g6g5','b0c2'])],exerciseIds:[]},
  {id:'rook-open-file',chapterId:'rook',phase:'middle',title:'Theo dõi cả đường Xe',summary:'Đường trống, vật cản và quân bảo vệ phải được đọc cùng nhau.',difficulty:'beginner',sections:[
   section('Đọc từ điểm đi đến điểm đến','Ở hình này, các ô giữa hai Xe đều trống. Nước ăn quân được bộ luật cho phép; khi áp dụng vào ván đầy đủ vẫn phải kiểm tra nước đáp của đối thủ.',rook,['a2a7']),
   section('Từ một đường đến hai đường','Hai Xe có thể chia nhau khống chế hàng và cột. Ở hình tiếp theo, hãy quan sát đường dọc của Tướng Đỏ trước khi mở bài nhiều lượt.',palace,[]),
   section('Xe không nhảy qua quân','Tốt Đỏ ở c3 chặn đường ngang của Xe từ a3. Xe không thể đi xuyên qua quân mình để bắt Xe Đen ở g3; bộ luật chỉ cho phép các nước được liệt kê từ vị trí này.',rookBlocked,[])],exerciseIds:['v6-rooks-palace-a']},
  {id:'rook-support',chapterId:'rook',phase:'middle',title:'Quân nào giữ đường thoát',summary:'Đừng chỉ nhìn quân đang chiếu; kiểm tra quân nào đang bảo vệ nó.',difficulty:'intermediate',sections:[
   section('Quan sát nhiệm vụ của từng Xe','Hình này dùng hai Xe và đường khống chế của Tướng. Khi một Xe đổi hàng, đường thoát và quân Sĩ có thể thay đổi; phải tính lại sau mỗi phản ứng.',palace,['d4d9','e9e8','d9d8']),
   section('Đổi hướng để tiếp tục ép','Đây là đoạn tiếp theo của một chuỗi được kiểm tra bằng luật. Bài luyện riêng sẽ yêu cầu bạn tự thực hiện từng quyết định thay vì chỉ xem nước chạy.',palace,['d4d9','e9e8','d9d8','e8e9','g6e6','f9e8','d8d9'],'Chuỗi tự dựng đã kiểm tra chiếu hết; chưa qua chuyên gia hoặc Pikafish.')],exerciseIds:['v6-rooks-palace-a']},
  {id:'cannon-screen',chapterId:'cannon',phase:'middle',title:'Ngòi Pháo có thể thay đổi',summary:'Đếm ngòi ở thế hiện tại, rồi đếm lại sau phản ứng đối thủ.',difficulty:'beginner',sections:[
   section('Đúng một quân ở giữa','Mã b4 làm ngòi giữa Pháo b2 và Xe b7. Khi ăn quân, Pháo cần đúng một ngòi; khi đi không ăn, Pháo cần đường trống.',cannon,['b2b7']),
   section('Đừng ghi nhớ chỉ một hình','Quân ngòi có thể thuộc bên nào. Điều phải giữ lại là cách đếm vật cản và kiểm tra an toàn Tướng.',cannon,[]),
   section('Đếm lại sau khi ngòi rời đường','Mã b4 đi sang c6. Đường b2–b7 giờ không còn quân ngòi, vì vậy Pháo không thể ăn Xe ở b7 trong thế mới. Một nước hợp lệ có thể làm thay đổi hoàn toàn đường Pháo.',cannon,['b4c6'])],exerciseIds:[]},
  {id:'horse-path',chapterId:'horse',phase:'middle',title:'Mã đi được khi chân còn trống',summary:'Kiểm tra chân Mã trước, sau đó mới nhìn mục tiêu.',difficulty:'beginner',sections:[
   section('Tách chân Mã khỏi ô đến','Mã c3 đi đến d5 qua chân c4. Ô chân phải trống; một mục tiêu có vẻ gần không đồng nghĩa có đường đi hợp lệ.',horse,['c3d5']),
   section('Nhìn lại sau mỗi nước đáp','Một quân vừa di chuyển có thể mở hoặc chặn chân Mã. Đừng suy ra đòn đôi chỉ từ hình dạng quân; phải xác minh cả hai mục tiêu và phản ứng đối thủ.',horse,[]),
   section('Chân Mã bị chặn','Tốt Đỏ ở c4 chiếm chân của Mã c3. Nước c3–d5 không hợp lệ dù Xe Đen đang ở ô đích; hãy kiểm tra chân Mã trước khi tính quân bị ăn.',horseBlocked,[])],exerciseIds:[]},
  {id:'king-first',chapterId:'kingSafety',phase:'middle',title:'Giải chiếu trước khi làm việc khác',summary:'Nước hợp lệ phải giữ Tướng an toàn.',difficulty:'beginner',sections:[
   section('Nhìn đường chiếu','Xe Đen a0 đang chiếu Tướng Đỏ e0. Xe Đỏ có thể bắt quân đang chiếu. Trước khi chọn, hãy kiểm tra cả đường giữa hai quân.',safety,['a2a0']),
   section('Kiểm tra lại toàn bàn','Bắt quân chiếu, che đường hoặc di chuyển Tướng chỉ là các loại ý tưởng. Mỗi nước cụ thể vẫn phải qua luật; không có nút chữa chiếu dùng được cho mọi hình.',safety,[]),
   section('Một cách giải chiếu là chắn đường','Xe Đen e8 đang chiếu dọc cột e. Xe Đỏ đi a2–e2 để chắn đường chiếu; sau nước này bộ luật xác nhận Tướng Đỏ không còn bị chiếu. Trong thế khác, nước chắn có thể không hợp lệ nếu vẫn còn quân chiếu khác.',safetyBlock,['a2e2'])],exerciseIds:[]},
  {id:'rooks-palace',chapterId:'coordination',phase:'middle',title:'Hai Xe cùng ép trong cung',summary:'Theo dõi cả đường thoát và khả năng Sĩ che chiếu.',difficulty:'intermediate',sections:[
   section('Một quân tiến và một quân giữ','Bài luyện gắn với hình này có nhiều quyết định. Mục tiêu cụ thể là chiếu liên tục tới chiếu hết trong giới hạn bài, không phải khẳng định đây là kế hoạch duy nhất trong mọi thế tương tự.',palace,[]),
   section('Một phản ứng cần tính','Sau khi Xe bắt Sĩ, Tướng có thể đổi hàng. Người học phải tự đi tiếp; nước đầu đúng chưa hoàn thành cả bài.',palace,['d4d9','e9e8'])],exerciseIds:['v6-rooks-palace-a','v6-rooks-palace-b']},
  {id:'end-escape',chapterId:'end-basic',phase:'end',title:'Đếm đường thoát trước kết luận',summary:'Ít quân không tự chứng minh thắng hoặc hòa.',difficulty:'beginner',sections:[
   section('Kiểm tra ba điều','Tướng có đang bị chiếu không, có nước giải chiếu hợp lệ không, và bên đi còn nước hợp lệ nào khác không? Hãy kiểm tra trạng thái do bộ luật trả về thay vì kết luận chỉ từ số quân.',palace,['d4d9','e9e8','d9d8','e8e9','g6e6','f9e8','d8d9'],'Ví dụ chiếu hết cụ thể; không thay cho giáo trình tàn cuộc đầy đủ.')],exerciseIds:[]}
 ];
 const exercises=[
  {
    "id": "v6-rooks-palace-a",
    "version": 1,
    "format": "line-v1",
    "title": "Hai Xe khép vòng vây",
    "phase": "middle",
    "chapterId": "coordination",
    "skill": "safety",
    "pieceTags": [
      "rook",
      "king"
    ],
    "familyId": "two-rooks-palace-checking",
    "difficulty": "intermediate",
    "difficultyLabel": "Trung cấp · mức dự kiến",
    "goal": "Dùng chuỗi nước chiếu liên tục để chiếu hết trong tối đa 4 lượt đi của Đỏ.",
    "learner": "w",
    "fen": "3aka3/5R3/5R3/9/9/9/9/9/9/3K5 w",
    "root": "n0",
    "nodes": {
      "n0": {
        "id": "n0",
        "fen": "3aka3/5R3/5R3/9/9/9/9/9/9/3K5 w",
        "remaining": 4,
        "choices": [
          {
            "move": "f8f9",
            "reply": "e9e8",
            "next": "n1"
          }
        ],
        "rejectedMoves": [
          "f8g8",
          "f8h8",
          "f8i8",
          "f8e8",
          "f8d8",
          "f8c8",
          "f8b8",
          "f8a8",
          "f7g7",
          "f7h7",
          "f7i7",
          "f7e7",
          "f7d7",
          "f7c7",
          "f7b7",
          "f7a7",
          "f7f6",
          "f7f5",
          "f7f4",
          "f7f3",
          "f7f2",
          "f7f1",
          "f7f0",
          "d0d1"
        ]
      },
      "n1": {
        "id": "n1",
        "fen": "3a1R3/4k4/5R3/9/9/9/9/9/9/3K5 w",
        "remaining": 3,
        "choices": [
          {
            "move": "f9f8",
            "reply": "e8e9",
            "next": "n2"
          },
          {
            "move": "f7f8",
            "reply": "e8e7",
            "next": "n4"
          }
        ],
        "rejectedMoves": [
          "f9g9",
          "f9h9",
          "f9i9",
          "f9e9",
          "f9d9",
          "f7g7",
          "f7h7",
          "f7i7",
          "f7e7",
          "f7d7",
          "f7c7",
          "f7b7",
          "f7a7",
          "f7f6",
          "f7f5",
          "f7f4",
          "f7f3",
          "f7f2",
          "f7f1",
          "f7f0",
          "d0d1"
        ]
      },
      "n2": {
        "id": "n2",
        "fen": "3ak4/5R3/5R3/9/9/9/9/9/9/3K5 w",
        "remaining": 2,
        "choices": [
          {
            "move": "f7e7",
            "reply": "d9e8",
            "next": "n3"
          }
        ],
        "rejectedMoves": [
          "f8g8",
          "f8h8",
          "f8i8",
          "f8e8",
          "f8d8",
          "f8c8",
          "f8b8",
          "f8a8",
          "f8f9",
          "f7g7",
          "f7h7",
          "f7i7",
          "f7d7",
          "f7c7",
          "f7b7",
          "f7a7",
          "f7f6",
          "f7f5",
          "f7f4",
          "f7f3",
          "f7f2",
          "f7f1",
          "f7f0",
          "d0d1"
        ]
      },
      "n3": {
        "id": "n3",
        "fen": "4k4/4aR3/4R4/9/9/9/9/9/9/3K5 w",
        "remaining": 1,
        "choices": [
          {
            "move": "e7e8",
            "reply": null,
            "next": null
          }
        ],
        "rejectedMoves": [
          "f8g8",
          "f8h8",
          "f8i8",
          "f8e8",
          "f8f7",
          "f8f6",
          "f8f5",
          "f8f4",
          "f8f3",
          "f8f2",
          "f8f1",
          "f8f0",
          "f8f9",
          "e7f7",
          "e7g7",
          "e7h7",
          "e7i7",
          "e7d7",
          "e7c7",
          "e7b7",
          "e7a7",
          "e7e6",
          "e7e5",
          "e7e4",
          "e7e3",
          "e7e2",
          "e7e1",
          "e7e0",
          "d0e0",
          "d0d1"
        ]
      },
      "n4": {
        "id": "n4",
        "fen": "3a1R3/5R3/4k4/9/9/9/9/9/9/3K5 w",
        "remaining": 2,
        "choices": [
          {
            "move": "f9e9",
            "reply": "d9e8",
            "next": "n5"
          }
        ],
        "rejectedMoves": [
          "f9g9",
          "f9h9",
          "f9i9",
          "f9d9",
          "f8g8",
          "f8h8",
          "f8i8",
          "f8e8",
          "f8d8",
          "f8c8",
          "f8b8",
          "f8a8",
          "f8f7",
          "f8f6",
          "f8f5",
          "f8f4",
          "f8f3",
          "f8f2",
          "f8f1",
          "f8f0",
          "d0d1"
        ]
      },
      "n5": {
        "id": "n5",
        "fen": "4R4/4aR3/4k4/9/9/9/9/9/9/3K5 w",
        "remaining": 1,
        "choices": [
          {
            "move": "e9e8",
            "reply": null,
            "next": null
          }
        ],
        "rejectedMoves": [
          "e9f9",
          "e9g9",
          "e9h9",
          "e9i9",
          "e9d9",
          "e9c9",
          "e9b9",
          "e9a9",
          "f8g8",
          "f8h8",
          "f8i8",
          "f8e8",
          "f8f7",
          "f8f6",
          "f8f5",
          "f8f4",
          "f8f3",
          "f8f2",
          "f8f1",
          "f8f0",
          "f8f9",
          "d0d1"
        ]
      }
    },
    "exampleLine": [
      "f8f9",
      "e9e8",
      "f9f8",
      "e8e9",
      "f7e7",
      "d9e8",
      "e7e8"
    ],
    "decisions": 4,
    "source": "Cờ Chill tự dựng 2026-10-25",
    "proof": {
      "method": "exhaustive-checking-mate",
      "maximumPlies": 7,
      "defender": "all-legal-replies",
      "engine": "XQ legal rules",
      "expertReviewed": false,
      "pikafishVerified": false,
      "examined": 75
    },
    "verification": "Thế tự dựng. Đã kiểm tra đầy đủ phản ứng hợp lệ của Đen trong mục tiêu chiếu liên tục tối đa 4 lượt Đỏ; không phải kết quả Pikafish hay bài chuyên gia duyệt.",
    "what": "Hai Xe phối hợp ép Tướng trong cung, tận dụng đường khống chế của Tướng Đỏ.",
    "why": "Mỗi nước được chấp nhận tiếp tục chiếu và giữ được kết quả chiếu hết trong giới hạn bài trước mọi phản ứng hợp lệ của Đen. Đường trả lời được chọn để kéo dài khả năng chống đỡ trong mục tiêu này.",
    "how": "Đếm đường thoát của Tướng, kiểm tra khả năng bắt quân đang chiếu và nhìn cả quân phòng thủ trước khi đổi Xe hoặc chuyển hướng tấn công."
  },
  {
    "id": "v6-rooks-palace-b",
    "version": 1,
    "format": "line-v1",
    "title": "Đổi hướng trong cung",
    "phase": "middle",
    "chapterId": "coordination",
    "skill": "safety",
    "pieceTags": [
      "rook",
      "king"
    ],
    "familyId": "two-rooks-palace-checking",
    "difficulty": "intermediate",
    "difficultyLabel": "Trung cấp · mức dự kiến",
    "goal": "Dùng chuỗi nước chiếu liên tục để chiếu hết trong tối đa 4 lượt đi của Đỏ.",
    "learner": "w",
    "fen": "R1Raka3/9/9/9/9/9/9/9/9/3K5 w",
    "root": "n0",
    "nodes": {
      "n0": {
        "id": "n0",
        "fen": "R1Raka3/9/9/9/9/9/9/9/9/3K5 w",
        "remaining": 4,
        "choices": [
          {
            "move": "c9d9",
            "reply": "e9e8",
            "next": "n1"
          }
        ],
        "rejectedMoves": [
          "a9b9",
          "a9a8",
          "a9a7",
          "a9a6",
          "a9a5",
          "a9a4",
          "a9a3",
          "a9a2",
          "a9a1",
          "a9a0",
          "c9b9",
          "c9c8",
          "c9c7",
          "c9c6",
          "c9c5",
          "c9c4",
          "c9c3",
          "c9c2",
          "c9c1",
          "c9c0",
          "d0d1"
        ]
      },
      "n1": {
        "id": "n1",
        "fen": "R2R1a3/4k4/9/9/9/9/9/9/9/3K5 w",
        "remaining": 3,
        "choices": [
          {
            "move": "a9a8",
            "reply": "e8e7",
            "next": "n2"
          },
          {
            "move": "d9e9",
            "reply": "e8f8",
            "next": "n3"
          },
          {
            "move": "d9d8",
            "reply": "e8e7",
            "next": "n5"
          }
        ],
        "rejectedMoves": [
          "a9b9",
          "a9c9",
          "a9a7",
          "a9a6",
          "a9a5",
          "a9a4",
          "a9a3",
          "a9a2",
          "a9a1",
          "a9a0",
          "d9f9",
          "d9c9",
          "d9b9",
          "d9d7",
          "d9d6",
          "d9d5",
          "d9d4",
          "d9d3",
          "d9d2",
          "d9d1",
          "d0d1"
        ]
      },
      "n2": {
        "id": "n2",
        "fen": "3R1a3/R8/4k4/9/9/9/9/9/9/3K5 w",
        "remaining": 2,
        "choices": [
          {
            "move": "d9d7",
            "reply": null,
            "next": null
          }
        ],
        "rejectedMoves": [
          "d9e9",
          "d9f9",
          "d9c9",
          "d9b9",
          "d9a9",
          "d9d8",
          "d9d6",
          "d9d5",
          "d9d4",
          "d9d3",
          "d9d2",
          "d9d1",
          "a8b8",
          "a8c8",
          "a8d8",
          "a8e8",
          "a8f8",
          "a8g8",
          "a8h8",
          "a8i8",
          "a8a7",
          "a8a6",
          "a8a5",
          "a8a4",
          "a8a3",
          "a8a2",
          "a8a1",
          "a8a0",
          "a8a9",
          "d0d1"
        ]
      },
      "n3": {
        "id": "n3",
        "fen": "R3Ra3/5k3/9/9/9/9/9/9/9/3K5 w",
        "remaining": 2,
        "choices": [
          {
            "move": "e9f9",
            "reply": "f8e8",
            "next": "n4"
          }
        ],
        "rejectedMoves": [
          "a9b9",
          "a9c9",
          "a9d9",
          "a9a8",
          "a9a7",
          "a9a6",
          "a9a5",
          "a9a4",
          "a9a3",
          "a9a2",
          "a9a1",
          "a9a0",
          "e9d9",
          "e9c9",
          "e9b9",
          "e9e8",
          "e9e7",
          "e9e6",
          "e9e5",
          "e9e4",
          "e9e3",
          "e9e2",
          "e9e1",
          "e9e0",
          "d0e0",
          "d0d1"
        ]
      },
      "n4": {
        "id": "n4",
        "fen": "R4R3/4k4/9/9/9/9/9/9/9/3K5 w",
        "remaining": 1,
        "choices": [
          {
            "move": "a9e9",
            "reply": null,
            "next": null
          }
        ],
        "rejectedMoves": [
          "a9b9",
          "a9c9",
          "a9d9",
          "a9a8",
          "a9a7",
          "a9a6",
          "a9a5",
          "a9a4",
          "a9a3",
          "a9a2",
          "a9a1",
          "a9a0",
          "f9g9",
          "f9h9",
          "f9i9",
          "f9e9",
          "f9d9",
          "f9c9",
          "f9b9",
          "f9f8",
          "f9f7",
          "f9f6",
          "f9f5",
          "f9f4",
          "f9f3",
          "f9f2",
          "f9f1",
          "f9f0",
          "d0d1"
        ]
      },
      "n5": {
        "id": "n5",
        "fen": "R4a3/3R5/4k4/9/9/9/9/9/9/3K5 w",
        "remaining": 2,
        "choices": [
          {
            "move": "a9a7",
            "reply": null,
            "next": null
          }
        ],
        "rejectedMoves": [
          "a9b9",
          "a9c9",
          "a9d9",
          "a9e9",
          "a9f9",
          "a9a8",
          "a9a6",
          "a9a5",
          "a9a4",
          "a9a3",
          "a9a2",
          "a9a1",
          "a9a0",
          "d8e8",
          "d8f8",
          "d8g8",
          "d8h8",
          "d8i8",
          "d8c8",
          "d8b8",
          "d8a8",
          "d8d7",
          "d8d6",
          "d8d5",
          "d8d4",
          "d8d3",
          "d8d2",
          "d8d1",
          "d8d9",
          "d0d1"
        ]
      }
    },
    "exampleLine": [
      "c9d9",
      "e9e8",
      "d9e9",
      "e8f8",
      "e9f9",
      "f8e8",
      "a9e9"
    ],
    "decisions": 4,
    "source": "Cờ Chill tự dựng 2026-10-25",
    "proof": {
      "method": "exhaustive-checking-mate",
      "maximumPlies": 7,
      "defender": "all-legal-replies",
      "engine": "XQ legal rules",
      "expertReviewed": false,
      "pikafishVerified": false,
      "examined": 70
    },
    "verification": "Thế tự dựng. Đã kiểm tra đầy đủ phản ứng hợp lệ của Đen trong mục tiêu chiếu liên tục tối đa 4 lượt Đỏ; không phải kết quả Pikafish hay bài chuyên gia duyệt.",
    "what": "Hai Xe phối hợp ép Tướng trong cung, tận dụng đường khống chế của Tướng Đỏ.",
    "why": "Mỗi nước được chấp nhận tiếp tục chiếu và giữ được kết quả chiếu hết trong giới hạn bài trước mọi phản ứng hợp lệ của Đen. Đường trả lời được chọn để kéo dài khả năng chống đỡ trong mục tiêu này.",
    "how": "Đếm đường thoát của Tướng, kiểm tra khả năng bắt quân đang chiếu và nhìn cả quân phòng thủ trước khi đổi Xe hoặc chuyển hướng tấn công."
  }
];
 for(const lesson of lessons){lesson.source='Cờ Chill tự biên soạn 2026-10-25';lesson.verification='Minh họa được phát lại qua bộ luật; không có đánh giá tối ưu hoặc chứng nhận chuyên gia.';}
 function findLesson(id){return lessons.find(x=>x.id===id)||null;}
 function findExercise(id){return exercises.find(x=>x.id===id)||null;}
 function findChapter(id){return chapters.find(x=>x.id===id)||null;}
 function chapterProgress(chapterId,records){const chapter=findChapter(chapterId);if(!chapter)return null;const attempts=Array.isArray(records)?records:Object.values(records||{}).flatMap(r=>Array.isArray(r?.attempts)?r.attempts:r?[r]:[]);const completed=new Set(attempts.filter(a=>a&&a.success===true&&a.completedAt&&chapter.exerciseIds.includes(a.puzzleId||a.exerciseId)).map(a=>a.puzzleId||a.exerciseId));return {completed:completed.size,total:chapter.exerciseIds.length,required:10,level:completed.size>=10?2:1,thresholdMet:completed.size>=10,needsMoreContent:chapter.exerciseIds.length<10};}
 function validate(){for(const chapter of chapters)if(!Array.isArray(chapter.fixtureSkills)||chapter.fixtureSkills.some(skill=>!['material','cannon','horse','safety'].includes(skill)))throw new Error('Unknown chapter practice skill');for(const lesson of lessons){if(!findChapter(lesson.chapterId))throw new Error('Unknown lesson chapter');for(const diagram of lesson.sections){let pos=XQ.Position.fromFen(diagram.fen);for(const move of diagram.moves)pos=pos.play(move);}for(const id of lesson.exerciseIds)if(!findExercise(id))throw new Error('Unknown practice');}return true;}
 function freeze(value){if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.freeze(value);for(const child of Object.values(value))freeze(child);}return value;}
 validate();
 return freeze({courses,chapters,lessons,exercises,findLesson,findExercise,findChapter,chapterProgress,validate});
});
