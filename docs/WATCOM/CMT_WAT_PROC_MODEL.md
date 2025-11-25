 OMF COMENT Class 0x9B (CMT_WAT_PROC_MODEL)

  What It Is

  COMENT class 0x9B is a Watcom-specific extension to the Intel OMF (Object Module Format) that embeds compiler parameters into the object file. It tells linkers and other tools what processor and memory model the code was compiled for.

  The constant is defined in bld/watcom/h/pcobj.h:270:
  CMT_WAT_PROC_MODEL  = 0x9b, /* Watcom processor & model info */

  There's also a Microsoft equivalent at class 0x9D (CMT_MS_PROC_MODEL) with the same format.

  ---
  Record Structure

  The OMF COMENT record has this layout:

  | Offset | Size | Field         | Value                     |
  |--------|------|---------------|---------------------------|
  | 0      | 1    | Record type   | 0x88 (CMD_COMENT)         |
  | 1      | 2    | Record length | varies                    |
  | 3      | 1    | Comment type  | 0x80 (CMT_TNP - no purge) |
  | 4      | 1    | Comment class | 0x9B                      |
  | 5+     | 4-5  | Data          | Processor/model string    |
  | last   | 1    | Checksum      |                           |

  The data payload is a 4-5 character string:

  | Byte | Field          | Values                                                                        |
  |------|----------------|-------------------------------------------------------------------------------|
  | 0    | Processor      | '0' = 8086, '2' = 80286, '3' = 80386+                                         |
  | 1    | Memory Model   | 's' = small, 'm' = medium, 'c' = compact, 'l' = large, 'h' = huge, 'f' = flat |
  | 2    | Optimization   | 'O' = optimized (always 'O' - historical Microsoft convention)                |
  | 3    | Floating Point | 'e' = emulated inline, 'c' = emulator calls, 'p' = 80x87 inline               |
  | 4    | (optional)     | 'd' = default, 'i' = position independent code                                |

  ---
  How It's Generated (Code Generator)

  From bld/cg/intel/c/x86obj.c:975-1004:

  static void OutModel( array_control *dest )
  {
      char model[6];

      if( _CPULevel( CPU_386 ) ) {
          model[0] = '3';
      } else if( _CPULevel( CPU_286 ) ) {
          model[0] = '2';
      } else {
          model[0] = '0';
      }
      model[1] = GetMemModel();  // Returns 's', 'm', 'c', 'l', 'h', or 'f'
      model[2] = 'O';            // "Why? Ask microsoft!"
      if( _FPULevel( FPU_87 ) ) {
          if( _IsEmulation() ) {
              model[3] = 'e';
          } else {
              model[3] = 'p';
          }
      } else {
          model[3] = 'c';
      }
      model[4] = 'd';
      if( _IsModel( CGSW_GEN_POSITION_INDEPENDANT ) ) {
          model[4] = 'i';
      }
      model[5] = '\0';
      OutString( model, dest );
  }

  The record is emitted with:
  OutShort( MODEL_COMMENT, names );  // MODEL_COMMENT = CMT_NP( WAT_PROC_MODEL )
  OutModel( names );
  PutObjOMFRec( CMD_COMENT, names );

  ---
  How It's Read (Linker)

  From bld/wl/c/objomf.c:932-937:

  case CMT_WAT_PROC_MODEL:
  case CMT_MS_PROC_MODEL:
      proc = *ObjBuff - '0';        // Convert ASCII digit to number
      if( proc > FmtData.cpu_type )
          FmtData.cpu_type = proc;  // Track highest CPU level required
      break;

  The linker uses this to determine the minimum CPU level required for the final executable.

  ---
  How It's Read (ORL Library)

  From bld/orl/omf/c/omfload.c:417-438:

  case CMT_WAT_PROC_MODEL:
      ofh->status |= OMF_STATUS_WATCOM;
      /* fall through */
  case CMT_MS_PROC_MODEL:
      if( len == 0 )
          break;
      switch( *buffer ) {
      case '2':
      case '0':
          ofh->machine_type = ORL_MACHINE_TYPE_I8086;
          _SetWordSize( ofh->flags, ORL_FILE_FLAG_16BIT_MACHINE );
          break;
      case '3':
      default:
          ofh->machine_type = ORL_MACHINE_TYPE_I386;
          _SetWordSize( ofh->flags, ORL_FILE_FLAG_32BIT_MACHINE );
          break;
      }
      break;

  ---
  Implementation Example (Reading)

  To implement support for reading this record:

  #include <stdint.h>
  #include <stdbool.h>

  typedef struct {
      uint8_t processor;      // 0=8086, 2=286, 3=386+
      char    mem_model;      // 's','m','c','l','h','f'
      bool    optimized;
      char    fp_mode;        // 'e','c','p'
      bool    pic;            // position independent
  } watcom_proc_model_t;

  bool parse_coment_0x9b(const uint8_t *data, size_t len, watcom_proc_model_t *out)
  {
      if (len < 4)
          return false;

      // Processor: '0', '2', or '3'
      out->processor = data[0] - '0';

      // Memory model
      out->mem_model = data[1];

      // Optimization (byte 2 is always 'O')
      out->optimized = (data[2] == 'O');

      // Floating point mode
      out->fp_mode = data[3];

      // Position independent (optional byte 4)
      out->pic = (len >= 5 && data[4] == 'i');

      return true;
  }

  ---
  Implementation Example (Writing)

  void emit_coment_0x9b(FILE *obj, int cpu, char model, char fp_mode, bool pic)
  {
      uint8_t record[12];
      int i = 0;

      record[i++] = 0x88;         // CMD_COMENT
      record[i++] = 0x00;         // length low (fill later)
      record[i++] = 0x00;         // length high (fill later)
      record[i++] = 0x80;         // CMT_TNP (no purge)
      record[i++] = 0x9B;         // CMT_WAT_PROC_MODEL

      // Data payload
      record[i++] = (cpu >= 386) ? '3' : (cpu >= 286) ? '2' : '0';
      record[i++] = model;        // 's','m','c','l','h','f'
      record[i++] = 'O';          // optimization flag
      record[i++] = fp_mode;      // 'e','c','p'
      record[i++] = pic ? 'i' : 'd';

      // Fill in length (excludes record type and checksum)
      uint16_t len = i - 3 + 1;   // +1 for checksum
      record[1] = len & 0xFF;
      record[2] = (len >> 8) & 0xFF;

      // Calculate checksum
      uint8_t checksum = 0;
      for (int j = 0; j < i; j++)
          checksum += record[j];
      record[i++] = -checksum;    // Two's complement

      fwrite(record, 1, i, obj);
  }
