package ngz.markov;

import lombok.Getter;
import ngz.markov.utils.MapUtils;
import org.apache.flink.util.ParameterTool;

import java.util.Map;

@Getter
public class JobConfig {

    private final ParameterTool jobParams ;
    private final String pipelineName;

    private final String eventClassName;

    private final Map<String,String> eventParams;

    private final String sinkType ;
    private final Map<String,String> sinkParams;

    public JobConfig(String[] args){

        ParameterTool params = ParameterTool.fromArgs(args);

        this.jobParams = params ;

        this.pipelineName = params.getRequired("pipeline.name");
        this.eventClassName = params.getRequired("event.class");

        Map<String,String> paramsMap = params.toMap();
        this.eventParams = MapUtils.subMap(paramsMap,"event.");

        this.sinkType = params.getRequired("sink.type");
        this.sinkParams = MapUtils.subMap(paramsMap, "sink." + sinkType + "." );
    }
}
