#include "md5.h"

void	md5Finalize(t_md5 *md5)
{
	uint32_t		input[16];
	unsigned int	offset;
	unsigned int	paddingLength;

	offset = md5->inputSizeInBytes % 64;
	paddingLength = offset < 56 ? 56 - offset : (56 + 64) - offset;
	md5Update(md5, PADDING, paddingLength);
	md5->inputSizeInBytes -= (uint64_t)paddingLength;
	for(unsigned int j = 0; j < 14; ++j)
	{
		input[j] = (uint32_t)(md5->nextStepInput[(j * 4) + 3]) << 24 |
				(uint32_t)(md5->nextStepInput[(j * 4) + 2]) << 16 |
				(uint32_t)(md5->nextStepInput[(j * 4) + 1]) <<  8 |
				(uint32_t)(md5->nextStepInput[(j * 4)]);
	}
	input[14] = (uint32_t)(md5->inputSizeInBytes * 8);
	input[15] = (uint32_t)((md5->inputSizeInBytes * 8) >> 32);

	md5Step(md5->hashAccumulator, input);
	for(unsigned int i = 0; i < 4; ++i)
	{
		md5->result[(i * 4) + 0] = (uint8_t)((md5->hashAccumulator[i] & 0x000000FF));
		md5->result[(i * 4) + 1] = (uint8_t)((md5->hashAccumulator[i] & 0x0000FF00) >>  8);
		md5->result[(i * 4) + 2] = (uint8_t)((md5->hashAccumulator[i] & 0x00FF0000) >> 16);
		md5->result[(i * 4) + 3] = (uint8_t)((md5->hashAccumulator[i] & 0xFF000000) >> 24);
	}
}

void	md5Step(uint32_t *hashAccumulator, uint32_t *input)
{
	uint32_t		AA = hashAccumulator[0];
	uint32_t		BB = hashAccumulator[1];
	uint32_t		CC = hashAccumulator[2];
	uint32_t		DD = hashAccumulator[3];
	uint32_t		E;
	uint32_t		temp;
	unsigned int	j;
	unsigned int	i;

	for(i = 0; i < 64; ++i)
	{
		switch(i / 16)
		{
			case 0:
				E = F(BB, CC, DD);
				j = i;
				break;
			case 1:
				E = G(BB, CC, DD);
				j = ((i * 5) + 1) % 16;
				break;
			case 2:
				E = H(BB, CC, DD);
				j = ((i * 3) + 5) % 16;
				break;
			default:
				E = I(BB, CC, DD);
				j = (i * 7) % 16;
				break;
		}
		temp = DD;
		DD = CC;
		CC = BB;
		BB = BB + LEFT_ROTATE((AA + E + K[i] + input[j]), S[i]);
		AA = temp;
	}
	hashAccumulator[0] += AA;
	hashAccumulator[1] += BB;
	hashAccumulator[2] += CC;
	hashAccumulator[3] += DD;
}

void	md5Update(t_md5 *md5, uint8_t *inputBuffer, size_t inputLen)
{
	uint32_t		input[16];
	unsigned int	offset;
	unsigned int	i;
	unsigned int	j;

	offset = md5->inputSizeInBytes % 64;
	md5->inputSizeInBytes += (uint64_t)inputLen;
	for(i = 0; i < inputLen; ++i)
	{
		md5->nextStepInput[offset++] = (uint8_t)*(inputBuffer + i);
		if(offset % 64 == 0)
		{
			for(j = 0; j < 16; ++j)
			{
				input[j] = (uint32_t)(md5->nextStepInput[(j * 4) + 3]) << 24 |
						(uint32_t)(md5->nextStepInput[(j * 4) + 2]) << 16 |
						(uint32_t)(md5->nextStepInput[(j * 4) + 1]) <<  8 |
						(uint32_t)(md5->nextStepInput[(j * 4)]);
			}
			md5Step(md5->hashAccumulator, input);
			offset = 0;
		}
	}
}

void	md5Init(t_md5 *md5)
{
	md5->hashAccumulator[0] = (uint32_t)A;
	md5->hashAccumulator[1] = (uint32_t)B;
	md5->hashAccumulator[2] = (uint32_t)C;
	md5->hashAccumulator[3] = (uint32_t)D;
}

uint8_t*	md5(char *input)
{
	uint8_t	*result;
	t_md5	md5;
	
	bzero(&md5, sizeof(md5));
	md5Init(&md5);
	md5Update(&md5, (uint8_t *)input, strlen(input));
	md5Finalize(&md5);

	result = md5.result;
	//printHash(result);
	return (result);
}

void printHash(uint8_t *p)
{
	for(unsigned int i = 0; i < 16; ++i)
		printf("%02x", p[i]);
	printf("\n");
}
