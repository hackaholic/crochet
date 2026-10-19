import {afterEach,expect,it,vi} from 'vitest';
import {verifyMockPayment,type PaymentIntent} from './payments';
afterEach(()=>vi.unstubAllGlobals());
const intent:PaymentIntent={paymentId:1,orderId:2,orderNumber:'test-order',provider:'mock',providerOrderId:'mock_order_1',amount:20,amountPaise:2000,currency:'INR'};
it('never sends mock verification for a real or unknown provider',async()=>{
 const request=vi.fn();vi.stubGlobal('fetch',request);
 for(const provider of ['razorpay','unknown','']) await expect(verifyMockPayment({...intent,provider},'test')).rejects.toThrow('secure gateway checkout');
 expect(request).not.toHaveBeenCalled();
});
it('retains explicit mock-provider simulation and surfaces verification failure',async()=>{
 const request=vi.fn().mockResolvedValueOnce({ok:true}).mockResolvedValueOnce({ok:false,status:400});vi.stubGlobal('fetch',request);
 await verifyMockPayment(intent,'Mock QA');
 expect(JSON.parse(request.mock.calls[0][1].body)).toMatchObject({paymentId:1,providerOrderId:'mock_order_1'});
 await expect(verifyMockPayment(intent,'Mock QA')).rejects.toThrow('verification failed');
});
