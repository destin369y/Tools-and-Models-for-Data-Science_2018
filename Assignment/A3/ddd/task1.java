//COMP543, A3
//Destin Liu

import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.util.ToolRunner;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.conf.Configured;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class task1 extends Configured implements Tool {

  static int printUsage() {
    System.out.println("task1 [-m <maps>] [-r <reduces>] <input> <output>");
    ToolRunner.printGenericCommandUsage(System.out);
    return -1;
  }

  public static class task1Mapper
       extends Mapper<Object, Text, Text, DoubleWritable> {

    // so we don't have to do reallocations
    private final static DoubleWritable cost = new DoubleWritable(0);
    private Text word = new Text();

    // to check for only alphanumeric
    //String expression = "^[a-zA-Z]*$";
    //Pattern pattern = Pattern.compile(expression);

    public void map(Object key, Text value, Context context
                    ) throws IOException, InterruptedException {
    	
    	try{
        	//StringTokenizer itr = new StringTokenizer(value.toString());
        	String line = value.toString();
    		String[] arr = line.split(",");
    		String period = arr[9];
    		double nic = Double.parseDouble(arr[6]);
    		
    		word.set(period);
    		cost.set(nic);
        	context.write(word, cost);
    	} catch(Exception e) {
    		//throw exception
    	}
    	
    }
  }

  public static class task1Reducer
       extends Reducer<Text,DoubleWritable,Text,DoubleWritable> {
    private DoubleWritable result = new DoubleWritable();

    public void reduce(Text key, Iterable<DoubleWritable> values,
                       Context context
                       ) throws IOException, InterruptedException {
      double sumCost = 0;
      for (DoubleWritable val : values) {
    	  sumCost += val.get();
      }
      
      result.set(sumCost);
      context.write(key, result);
    }
  }

  public int run(String[] args) throws Exception {

    Configuration conf = new Configuration();
    Job job = Job.getInstance(conf, "task1");
    job.setJarByClass(task1.class);
    job.setMapperClass(task1Mapper.class);
    job.setCombinerClass(task1Reducer.class);
    job.setReducerClass(task1Reducer.class);
    job.setOutputKeyClass(Text.class);
    //job.setOutputValueClass(IntWritable.class);
    job.setOutputValueClass(DoubleWritable.class);
    
    List<String> other_args = new ArrayList<String>();
    for(int i=0; i < args.length; ++i) {
      try {
        if ("-r".equals(args[i])) {
          job.setNumReduceTasks(Integer.parseInt(args[++i]));
        } else {
          other_args.add(args[i]);
        }
      } catch (NumberFormatException except) {
        System.out.println("ERROR: Integer expected instead of " + args[i]);
        return printUsage();
      } catch (ArrayIndexOutOfBoundsException except) {
        System.out.println("ERROR: Required parameter missing from " +
                           args[i-1]);
        return printUsage();
      }
    }
    // Make sure there are exactly 2 parameters left.
    if (other_args.size() != 2) {
      System.out.println("ERROR: Wrong number of parameters: " +
                         other_args.size() + " instead of 2.");
      return printUsage();
    }
    FileInputFormat.setInputPaths(job, other_args.get(0));
    FileOutputFormat.setOutputPath(job, new Path(other_args.get(1)));
    return (job.waitForCompletion(true) ? 0 : 1);
  }
  
  public static void main(String[] args) throws Exception {
    int res = ToolRunner.run(new Configuration(), new task1(), args);
    System.exit(res);
  }

}
