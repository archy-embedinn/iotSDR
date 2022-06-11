#include "common.h"

typedef struct __attribute__((packed)) {
  s16 re;
  s16 im;
} fft_cplx_t;


int main(){

typedef struct __attribute__((packed)) {
  s16 re;
  s16 im;
} fft_cplx_t;

    static fft_cplx_t code_fft[32768];
    u32 fft_len = 32768

    float chips_per_sample = 1023 / 4*1023;

      gnss_signal_t sid = {
    .code = 1,
    .sat = CODE_GPS_L1CA,
  };

    code_resample(sid, chips_per_sample, code_fft, fft_len);

}


static void code_resample(gnss_signal_t sid, float chips_per_sample,
                            fft_cplx_t *resampled, u32 resampled_length)
    {
    const u8 *code = ca_code(sid);
    u32 code_length = CODE_LENGTH;

    float chip_offset = 0.0f;
    for (u32 i=0; i<resampled_length; i++) {
        u32 code_index = (u32)floorf(chip_offset);
        resampled[i] = (fft_cplx_t) {
        .re = CODE_MULT * get_chip((u8 *)code, code_index % code_length),
        .im = 0
        };
        chip_offset += chips_per_sample;
    }
}