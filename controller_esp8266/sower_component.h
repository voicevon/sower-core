#include "esphome.h"

class Sower_component : public Component {

 public:
  long raw_length = 0;
  long current_row = 0;
  long last_row = 0;
  char top_buffer[3];
  char plate[16];
  char plate_index = 0;
  char plate_index_last = 0;
  char crossed_row_map[3];
  

  void setup() override {

  }


  void loop() override {
    char plate_projection[3];
    for(i = 0, i < current_row, i++){
        plate_projection[i] = plate_map[current_row + i]
    }

    
    if (global.on_press){
        // 
        current_row = 0;
        plate_index++;
    }

    if (raw_length > 200){
        // time to release the buffer.

        // try to release rows from the first, to the second, to the third
        for(iRow=0, iRow<3, iRow++){ 
            release[iRow]= top_buffer[iRow] && crossed_row_map[iRow] 
        }


        current_row++;
        if (current_row > 16)
            current_row = 0
    }
    if (last_row == current_row)
        return;
    
 
      ESP_LOGD("sower", "new plate");
    }
  }
};