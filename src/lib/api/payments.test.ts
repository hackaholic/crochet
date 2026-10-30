import {afterEach,expect,it,vi} from 'vitest';
import {verifyCashfreePayment,verifyMockPayment,type PaymentIntent} from './payments';
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

it('rejects malformed Cashfree return identifiers before making a request',async()=>{
 const request=vi.fn();vi.stubGlobal('fetch',request);
 await expect(verifyCashfreePayment(0,'cf-order')).rejects.toThrow('details are invalid');
 await expect(verifyCashfreePayment(2_147_483_648,'cf-order')).rejects.toThrow('details are invalid');
 await expect(verifyCashfreePayment(5,'')).rejects.toThrow('details are invalid');
 await expect(verifyCashfreePayment(5,'x'.repeat(129))).rejects.toThrow('details are invalid');
 expect(request).not.toHaveBeenCalled();
});

it('asks the backend to verify the returned payment instead of trusting browser status',async()=>{
 const payment={id:5,orderId:9,orderNumber:'SLC-TEST-9',provider:'cashfree',providerOrderId:'cf-order-9',amount:600,amountPaise:60000,currency:'INR',status:'SUCCESS'};
 const request=vi.fn().mockResolvedValue({ok:true,json:async()=>payment});vi.stubGlobal('fetch',request);
 await expect(verifyCashfreePayment(5,'cf-order-9')).resolves.toEqual(payment);
 expect(request).toHaveBeenCalledOnce();
 expect(JSON.parse(request.mock.calls[0][1].body)).toEqual({paymentId:5,providerOrderId:'cf-order-9'});
});
